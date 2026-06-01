# Finesse 3 workshops

This is the repository to be used for Finesse workshops. The notebooks in it can change
depending on the event/audience. For the 'default introduction to Finesse interactive
examples, see the [getting started
repo](https://gitlab.com/ifosim/finesse/finesse3_getting_started)

## Run notebooks without installing Finesse

We provide two ways to 'try before you buy'. Both ways will stop your python session
after some time, so it is not suitable as a substitute for installation. You can always
download and save your work locally

### Google Colab

Click on the badge below to open this repository in Google Colab. You can then select
either of the notebooks to open and run them. This requires you to sign in to a Google
account. You can save copies of the notebooks in Google Drive.

[![Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gwoptics/finesse3_workshop)

### Binder

This is an alternative that does not require a Google account (can be a bit slower to
start up). It creates a [Jupyter](https://jupyter.org/) environment with Finesse 3
pre-installed.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/gwoptics/finesse3_workshop/HEAD)

## About

[Finesse 3](https://finesse.ifosim.org/) (Frequency domain INterfErometer Simulation
SoftwarE) is a fast and easy to use Python-based interferometer simulation program. It
uses frequency-domain optical modelling to build accurate quasi-static simulations of
arbitrary interferometer configurations.

## Get Finesse

If you decide to continue using Finesse, there are currently two options:

- [Finesse 3 installation
  instructions](https://finesse.ifosim.org/docs/latest/installing_finesse.html) for
  installing as a package
- [Finesse 3 developer
  guide](https://finesse.ifosim.org/docs/latest/developer/setting_up.html). for playing
  around with the source code

In either case, feel free to get in touch!

## Useful Resources

- [Finesse 3 homepage](https://finesse.ifosim.org/)
- [Finesse 3 documentation](https://finesse.ifosim.org/docs/latest/)
- [Finesse 3 source code](https://gitlab.com/ifosim/finesse/finesse3)

The review article [Interferometer Techniques for Gravitational-Wave
Detection](https://link.springer.com/article/10.1007/s41114-016-0002-8) is written by
some of the team behind Finesse and includes Finesse examples for many of the key topics
covered. It is therefore a good resource for those wanting to understand more about
interferometry as applied to gravitational-wave detection, and as implemented in
Finesse.

## Contact

For support and questions, use our [chat
channel](https://matrix.to/#/#finesse:matrix.org)

The [Ifosim logbooks](https://logbooks.ifosim.org/) provide a forum for users to share
more examples and references of interferometry simulations, mostly generated in the
course of gravitational-wave research. Posts are public; write-access is available for
all GW community members via albert.einstein, and to others on request. <!-- link 'on
request' somewhere? -->

General support is available by emailing us at finesse-support(at)nikhef.nl. If you have
trouble with installation or think you have encountered a bug, please include the
following information in your message:

- Operating System and installation method used
- versions of Finesse you are using
- [Minimum Working Example](https://en.wikipedia.org/wiki/Minimal_working_example) to
  reproduce the bug you encountered

## For maintainers

Note that this repo lives in two places:

- <https://gitlab.com/ifosim/finesse/finesse3_workshop>
- <https://github.com/gwoptics/finesse3_workshop>

The github exists only because it is required for Google Colab. The repository is
mirrored from gitlab -> github. All commits should be made on the gitlab repository and
will be synchronised to the github repo. You can start a manual synchronisation [in the
gitlab
settings](https://gitlab.com/ifosim/finesse/finesse3_workshop/-/settings/repository#js-push-remote-settings)
The github repo is configured to disallow any pushes. The mirroring depends on a
[PAT](https://github.com/organizations/gwoptics/settings/personal-access-tokens/766651)
that expires on Thu, Aug 13 2026
