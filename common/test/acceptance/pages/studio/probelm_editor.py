"""
Studio Problem Editor
"""
from common.test.acceptance.pages.studio.xblock_editor import XBlockEditorView
from common.test.acceptance.pages.common.utils import click_css
from selenium.webdriver.support.ui import Select


class ProblemXBlockEditorView(XBlockEditorView):
    """
    Represents the rendered view of an Problem editor.
    """

    editor_mode_css = '.edit-xblock-modal .editor-modes .editor-button'
    settings_mode = '.settings-button'

    def open_settings(self):
        """
        Clicks on the settings button
        """
        # self._click_button(self.settings_mode)
        self.click_css(self.settings_mode)

    @property
    def setting_keys(self):
        """
        Returns the list of all the keys
        """
        all_keys = self.q(css='.label.setting-label').text
        # We do not require the key for 'Component Location ID'
        all_keys.pop()
        return all_keys

    def set_field_val(self, field_display_name, field_value):
        """
        If editing, set the value of a field.
        """
        selector = '.xblock-studio_view li.field label:contains("{}") + input'.format(field_display_name)
        script = "$(arguments[0]).val(arguments[1]).change();"
        self.browser.execute_script(script, selector, field_value)

    def default_dropdown_value(self, css):
        """
        Gets default value from the dropdown
        Arguments:
            css(string): css of the dropdown for which default value is required
        Returns:
            dropdown_value(string): Default dropdown value
        """
        element = self.browser.find_element_by_css_selector(css)
        dropdown_default_selection = Select(element)
        value = dropdown_default_selection.first_selected_option.text
        return value

    def settings(self):
        """
        Default settings of problem
        Returns:
            settings_dict(dictionary): A dictionary of all the default settings
        """
        settings_dict = {}
        number_of_settings = len(self.q(css='.wrapper-comp-setting'))
        css = '.list-input.settings-list .field.comp-setting-entry'

        for index in range(number_of_settings):
            key = self.q(css=css + ':nth-of-type({}) label'.format(index + 1)).text[0]
            if self.q(css=css + ":nth-of-type({}) input".format(index + 1)).present:
                value = self.q(css=css + ":nth-of-type({}) input".format(index + 1)).attrs('value')[0]
            elif self.q(css=css + ":nth-of-type({}) select".format(index + 1)).present:
                value = self.default_dropdown_value(css + ':nth-of-type({}) select'.format(index + 1))
            settings_dict[key] = value

        return settings_dict

    def is_latex_compiler_present(self):
        """
        Checks for the presence of latex compiler settings presence
        Returns:
            bool: True if present
        """
        return self.q(css='.launch-latex-compiler').present

    def _click_button(self, button_name):
        """
        Click on a button as specified by `button_name`

        Arguments:
            button_name (str): button name
        """
        self.q(css=button_name).first.click()
        self.wait_for_ajax()

    def save(self):
        """
        Clicks save button.
        """
        click_css(self, '.action-save')
