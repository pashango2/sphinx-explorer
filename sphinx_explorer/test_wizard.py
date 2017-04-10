from sphinx_explorer.wizard.apidoc_wizard import *


def main():
    import os
    import toml
    import sys

    app = QApplication(sys.argv)

    setting_path = os.path.abspath(os.path.join("..", "settings", "apidoc.toml"))
    settings = toml.load(setting_path)
    params_dict = toml.load(os.path.join("..", "settings", "params.toml"))
    params_dict.update(settings["params"])

    wizard = create_wizard(params_dict, {}, None)
    wizard.exec_()

    app.exec_()


if __name__ == "__main__":
    main()
