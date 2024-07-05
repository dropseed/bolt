from bolt.utils.regex_helper import _lazy_re_compile


def get_version(version=None):
    """Return a PEP 440-compliant version number from VERSION."""

    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|rc}N - for alpha, beta, and rc releases

    main = get_main_version(version)

    # sub = ""
    # if version[3] == "alpha" and version[4] == 0:
    #     git_changeset = get_git_changeset()
    #     if git_changeset:
    #         sub = ".dev%s" % git_changeset

    # elif version[3] != "final":
    #     mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
    #     sub = mapping[version[3]] + str(version[4])

    return main


def get_main_version(version=None):
    """Return main version (X.Y[.Z]) from VERSION."""
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    return ".".join(str(x) for x in version[:parts])


def get_complete_version(version=None):
    """
    Return a tuple of the Bolt version. If version argument is non-empty,
    check for correctness of the tuple provided.
    """
    if version is None:
        from bolt.runtime import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ("alpha", "beta", "rc", "final")

    return version


version_component_re = _lazy_re_compile(r"(\d+|[a-z]+|\.)")


def get_version_tuple(version):
    """
    Return a tuple of version numbers (e.g. (1, 2, 3)) from the version
    string (e.g. '1.2.3').
    """
    version_numbers = []
    for item in version_component_re.split(version):
        if item and item != ".":
            try:
                component = int(item)
            except ValueError:
                break
            else:
                version_numbers.append(component)
    return tuple(version_numbers)