
import finesse
from finesse.analysis import actions as fac
import numpy as np
import matplotlib.pyplot as plt


#Helper function to check the resonance conditions and fix the modulation frequencies to  WIP
def adjust_modulation_freqs(model):
    """
    Adjust fmod frequencies so that they respect PRC resonance conditions (generally better to tune PRC length, see adjust_PRC_length function)
    """    
    print("-- adjusting f1 frequency")
    ftmp = 0.5 * model.fsr_PRC.value  # To remain around 6 MHz we need to have 7.5*FSR I'm Confusion
    #if short_or_long == 'long':
    #    print('Long recycling cavities mode, f1 set to 7.5 FSR')
    #    ftmp = ftmp.eval()*15
    #elif short_or_long == 'short':
    print('Short recycling cavities mode, f1 set to ????') 
    ftmp = ftmp.eval()
    #else:
    #    raise ValueError('short_or_long needs to be either "short" or "long"')
    
    f1 = model.eom1.f.value # works also for legacy
    print("   Adusting f1 by {:.4g}Hz".format(ftmp - f1))
    model.eom1.f.value = ftmp
    print("New f1 is {:.6g}Hz".format(ftmp))
    
    # Set f2 to 9*f1
    f2 = model.eom2.f.value
    print("   Adusting f2 by {:.4g}Hz".format((9*ftmp - f2)))
    model.eom2.f.value = 9*ftmp
    print("New f2 is {:.6g}Hz".format(9*ftmp))
    
    
def rc_length(model: finesse.Model, cavity: str, verbose: bool = False):
    """
    Obtain Power or Signal Recycling Cavity length.
    l_prc = l_pr+(l_n+l_w)/2
    l_src = l_sr+(l_n+l_w)/2

    Parameters
    ----------
    model : finesse.Model
            model of the interferometer.
    cavity : str
            Cavity name. Valid options are:
            - "PRC" (Power Recycling Cavity)
            - "SRC" (Signal Recycling Cavity)
            Case-insensitive.

    Returns
    -------
    l_rc : float
            Cavity length.
    """
    cavity = cavity.upper()
    path_ln = model.path(model.BS.p3.o, model.NI.p1.i)
    l_ln = path_ln.optical_length.eval()
    path_lw = model.path(model.BS.p2.o, model.WI.p1.i)
    l_lw = path_lw.optical_length.eval()
    if cavity == "PRC":
        
        path_pr = model.path(model.PR.p2.o, model.BS.p1.i)
        l_pr = path_pr.optical_length.eval()
        l_rc = l_pr + (l_ln + l_lw) / 2
    elif cavity == "SRC":
        path_sr = model.path(model.SR.p1.o, model.BS.p4.i)
        l_sr = path_sr.optical_length.eval()
        l_rc = l_sr + (l_ln + l_lw) / 2
    else:
        raise ValueError(f"Invalid cavity name: {cavity}. Choose 'PRC' or 'SRC'.")

    #if 
    if verbose:
        print(f"Current RC length is: {l_rc}")
    return l_rc


def adjust_rc_length(model: finesse.Model, cavity: str, verbose: bool = False):
    """
    Adjust PRC or SRC length so that it fulfils the requirement
    l_PRC = l_SRC = 0.5 * c / (2 * f1)=11.952, see TDR 2.3

    Parameters
    ----------
    model : finesse.Model
            model of the interferometer.
    cavity : str
            Cavity name. Valid options are:
            - "PRC" (Power Recycling Cavity)
            - "SRC" (Signal Recycling Cavity)
            Case-insensitive.

    Returns
    -------
    delta_l : float
            Cavity length adjustment.
    """
    from finesse.symbols import CONSTANTS
    cavity = cavity.upper()

    #f1 = model.eom1.f.value.eval()
    f1 = model.f1.value
    if verbose:
        print(f"——  adjusting {cavity} length")

    # calculate the required adjustment
    tmp = 0.5 * CONSTANTS["c0"] / (2 * f1)
    
    if cavity == "PRC":
        l_prc = rc_length(model, cavity, verbose= False)
        delta_l = tmp.eval() - l_prc
        # apply the adjustment
        model.lPOP_BS.L += delta_l
        if verbose:
            print(f"    adjusting lPOP_BS.L by {delta_l:.4g} m")
            
    elif cavity == "SRC":
        l_src = rc_length(model, cavity)
        delta_l = tmp.eval() - l_src
        # apply the adjustment
        model.lsr.L += delta_l
        if verbose:
            print(f"    adjusting lsr.L by {delta_l:.4g} m")
            
    else:
        raise ValueError(f"Invalid cavity name: {cavity}. Choose 'PRC' or 'SRC'.")

    return delta_l
    
    
def print_length(ifo):
    f1 = float(ifo.eom1.f.value)
    f2 = float(ifo.eom2.f.value)
    #f3 = float(ifo.eom3.f.value)
    print(f"""
┌───────────────────────────────────────────────────┐
│- Arm lengths [m]:                                 │
│  L = {ifo.elements["sarm"].L.value:<40.4f}     │
├───────────────────────────────────────────────────┤
│- Michelson and recycling lengths [m]:             │
│                                                   |
│  lPRC = {float(ifo.lPRC.value):<40.4f}  │
├───────────────────────────────────────────────────┤
│- Associated cavity frequencies [Hz]:              │
│  fsrArm = {float(ifo.fsr_arm.value):<38.2f}  │
│  fsrPRC = {float(ifo.fsr_PRC.value):<38.2f}  │
│                                                   │
│- Modulation sideband frequencies [MHz]:           │
│  f1     = {f1/1e6:<38.6f}  │
│  f2     = {f2/1e6:<38.6f}  │
├───────────────────────────────────────────────────┤
│- Check frequency match [MHz]:                     │
│  125.5*fsrArm-300 = {(125.5*float(ifo.fsr_arm.value)-300)/1e6:<30.6f}│
│  0.5*fsrPRC       = {0.5*float(ifo.fsr_PRC.value)/1e6:<30.6f}│
│  9*f1             = {9*f1/1e6:<30.6f}│
└───────────────────────────────────────────────────┘
""")


def print_tunings(ifo):
    # not sure if RM1 RM2 and RM3 should be just summed or what
    print(f"""
┌──────────────────┐
│ Optic     Tuning │
├──────────────────┤
│ PR  :  {ifo.RM1.phi.eval() + ifo.RM2.phi.eval() + ifo.RM3.phi.eval() + ifo.PRCL.DC:9.4g} │
│ ITM :  {ifo.ITM.phi.eval():9.4g} │
│ ETM :  {ifo.ETM.phi.eval() + ifo.ETM_z.DC:9.4g} │
└──────────────────┘""")
    
    
def print_powers(ifo):
    act = fac.Series(
        fac.Temporary(fac.Change({"eom1.midx": 0, "eom2.midx": 0}),
            fac.Noxaxis()
        )
    )
    out=ifo.run(act)
    #out = actions.temporary(noxaxis(ifo)
    print("""┌────────────────────────────────────────┐
│ Detector         Power [W]  Pow. ratio │
├────────────────────────────────────────┤""")
    for detector in ifo.detectors:
        power = np.abs(out[detector])**2
        if "CAR_AMP" in detector.name:
            print(f"│ {detector.name:12s}  :  {power:9.4g}  {power/ifo.laser1.P:9.4g}  │")
    print("└────────────────────────────────────────┘")



def cav_prop_trace(sol, prop):    
    """
    This function takes the solution 'sol' of the beam tracing 
    tool and the desired property 'prop' chosen among:
    
    - 'beamsize'
    - 'gouy'
    - 'curvature'
    
    and gives that property's evolution along the cavity axis. 
    It's the same vector plotted by the propagate_beam() tool.    
    """
    
    return list(sol.all_segments().items())[-1][1][1][prop]

def cart2pol(x, y):
    """Convert from Cartesian to polar coordinates.

    Example
    -------
    >>> theta, radius = pol2cart(x, y)
    """
    radius = np.hypot(x, y)
    theta = np.arctan2(y, x)
    return theta, radius


def compass(u, v, arrowprops=None):
    """
    Compass draws a graph that displays the vectors with
    components `u` and `v` as arrows from the origin.

    Examples
    --------
    >>> import numpy as np
    >>> u = [+0, +0.5, -0.50, -0.90]
    >>> v = [+1, +0.5, -0.45, +0.85]
    >>> compass(u, v)
    """

    angles, radii = cart2pol(u, v)
    fig, ax = plt.subplots(subplot_kw=dict(polar=True))

    kw = dict(arrowstyle="->")
    if arrowprops:
        kw.update(arrowprops)
    [ax.annotate("", xy=(angle, radius), xytext=(0, 0),
                 arrowprops=kw) for
     angle, radius in zip(angles, radii)]

    ax.set_ylim(0, np.max(radii))
    return fig, ax


def get_QNLS(model, axis=[10, 1000, 500]):
    kat = model.deepcopy()
    kat.parse(
        """
        # Differentially modulate the arm lengths
        fsig(1)
        sgen darmx sNarm.h
        sgen darmy sWarm.h phase=180

        # Output the full quantum noise limited sensitivity
        qnoised NSR_with_RP SRM1.p2.o nsr=True

        # Output just the shot noise limited sensitivity
        qshot NSR_without_RP SRM1.p2.o nsr=True
        """        
    )

    return kat.run(f'xaxis(darmx.f, "log", {axis[0]}, {axis[1]}, {axis[2]})')

def dof_plot_rf(model, dof, detector, axis=[-1, 1, 100], xscale=1, logy=True):
    kat = model.deepcopy()
    axis = np.array(axis, dtype=np.float64)
    axis[:2] *= xscale
    out = kat.run(fac.Xaxis(eval("kat."+dof+".DC"), "lin", *axis, relative=True))
    fig, ax = plt.subplots(1,1, figsize=(5,3))    
          
    ax.plot(out.x[0], out[detector+'_I'], label=detector+"_I", linestyle='-')
    ax.plot(out.x[0], out[detector+'_Q'], label=detector+"_Q", linestyle='--')
    ax.set_title(dof + ' DC scan')
    ax.set_xlabel(dof + ' DC')
    ax.set_ylabel(r'Amplitude $[\sqrt{W}]$')
    ax.legend(ncol=2)
    ax.grid(True)
    fig.set_tight_layout(True)
    return out


def get_dxdy(kat, bp, port, f="0"):
    # this function takes a kat file (should already contain a misalignment and be locked afterwards), 
    # a beam tracing output (bp = some_kat.beam_trace()) and a port attached to a mirror where the de-
    # centering is computed. 
    #
    # It attaches the necessary ADs to a temporary copy of the kat file and runs a 1-point simulation,
    # then returns the dx/dy decentering.

    if f not in ["0", "eom1.f", "eom2.f", "eom3.f"]:
        raise ValueError(f"Invalid value for f: {f}. Expected one of ['0', 'eom1.f', 'eom2.f', 'eom3.f'].")     
    
    mir = port.split(".")[0]    
    tmp_kat = kat.deepcopy()      

    tmp_kat.parse(f"""
    ad {mir}_00 {port} {f} 0 0
    ad {mir}_10 {port} {f} 1 0
    ad {mir}_01 {port} {f} 0 1
    """)

    tmp_kat.parse("noxaxis(pre_step=none, post_step=none, name='noxaxis')")
    out = tmp_kat.run()    
    
    dx = abs(out[f"{mir}_10"])/abs(out[f"{mir}_00"]) * bp[f"{port}"][0].w*1e6 * np.cos(np.angle(out[f"{mir}_10"])-np.angle(out[f"{mir}_00"]))
    dy = abs(out[f"{mir}_01"])/abs(out[f"{mir}_00"]) * bp[f"{port}"][1].w*1e6 * np.cos(np.angle(out[f"{mir}_01"])-np.angle(out[f"{mir}_00"]))

    return dx, dy


def make_SoS_QDs(Bx, kat, freq):     
    # This function generates QDs, attached to the Bx port, at a certain 'freq' frequency  
    # that should be as a beat note between sidebands. It adds the commands for finesse 
    # to track the beat note and  also the _DC QDs used to tune the demodulation phase. 
    #
    # The kat file should already contain the Bx_nf/ff_ports attached to appropriate telescopes.

    kat.add_frequency(freq)
    kat.add_frequency(-freq)

    kat.parse(f"""    
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_I {Bx}_nf_port.p1.i f={freq:.0f} phase=90  pdtype=xsplit
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_Q {Bx}_nf_port.p1.i f={freq:.0f} phase=0   pdtype=xsplit
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_I_DC {Bx}_nf_port.p1.i f={freq:.0f} phase=90 
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_Q_DC {Bx}_nf_port.p1.i f={freq:.0f} phase=0  
    
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_I {Bx}_ff_port.p1.i f={freq:.0f} phase=90  pdtype=xsplit
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_Q {Bx}_ff_port.p1.i f={freq:.0f} phase=0   pdtype=xsplit
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_I_DC {Bx}_ff_port.p1.i f={freq:.0f} phase=90 
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_Q_DC {Bx}_ff_port.p1.i f={freq:.0f} phase=0       
    """)

def make_2f_QDs(Bx, kat, freq):  
    # This function generates QDs at twice the 'freq' frequency, attached to the Bx port.
    #
    # The kat file should already contain the Bx_nf/ff_ports attached to appropriate telescopes.

    kat.parse(f"""     
    pd1 {Bx}_nf_{2*freq*1e-6:.0f}MHz_I {Bx}_nf_port.p1.i f={2*freq:.0f} phase=90  pdtype=xsplit
    pd1 {Bx}_nf_{2*freq*1e-6:.0f}MHz_Q {Bx}_nf_port.p1.i f={2*freq:.0f} phase=0   pdtype=xsplit
    pd1 {Bx}_ff_{2*freq*1e-6:.0f}MHz_I {Bx}_ff_port.p1.i f={2*freq:.0f} phase=90  pdtype=xsplit
    pd1 {Bx}_ff_{2*freq*1e-6:.0f}MHz_Q {Bx}_ff_port.p1.i f={2*freq:.0f} phase=0   pdtype=xsplit      
    """)


def get_gouy(solution): 
    # This function extract the accumulated gouy from the solution of the finesse tracing tool.
    # The beam should be traced from on of the ITMs towards the recycling mirror.    
    segments = list(solution.all_segments().items())
    last_key, last_value = segments[-1]
    return last_value[1]['gouy'][-1]


def pd_info(model, pd_name):
    kat = model.deepcopy()
    for _ in kat.detectors:
        if _.name == pd_name:
            pd = _
    if hasattr(pd, 'f2'):
        return(f"{pd.name} -- f1: {pd.f1.eval()}, phi1: {pd.phase1}, f2: {pd.f2}, phi2: {pd.phase2}.")
    else:
        return(f"{pd.name} -- f1: {pd.f1.eval()}, phi1: {pd.phase1}.")


def make_SoS_QDs(Bx, kat, freq):     
    # This function generates QDs, attached to the Bx port, at a certain 'freq' frequency  
    # that should be as a beat note between sidebands. It adds the commands for finesse 
    # to track the beat note and  also the _DC QDs used to tune the demodulation phase. 
    #
    # The kat file should already contain the Bx_nf/ff_ports attached to appropriate telescopes.

    kat.add_frequency(freq)
    kat.add_frequency(-freq)

    kat.parse(f"""    
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_I {Bx}_nf_port.p1.i f={freq:.0f} phase=90  pdtype=xsplit
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_Q {Bx}_nf_port.p1.i f={freq:.0f} phase=0   pdtype=xsplit
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_I_DC {Bx}_nf_port.p1.i f={freq:.0f} phase=90 
    pd1 {Bx}_nf_{freq*1e-6:.0f}MHz_Q_DC {Bx}_nf_port.p1.i f={freq:.0f} phase=0  
    
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_I {Bx}_ff_port.p1.i f={freq:.0f} phase=90  pdtype=xsplit
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_Q {Bx}_ff_port.p1.i f={freq:.0f} phase=0   pdtype=xsplit
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_I_DC {Bx}_ff_port.p1.i f={freq:.0f} phase=90 
    pd1 {Bx}_ff_{freq*1e-6:.0f}MHz_Q_DC {Bx}_ff_port.p1.i f={freq:.0f} phase=0       
    """)





