######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import re
import logging
from typing import Any
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
import requests
from compare3 import expect

# Constants for HTTP status codes and timeout
HTTP_200_OK = 200
WAIT_TIMEOUT = 10


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, 'Home Page')


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@then('I should see "{text}" in the item results table')
def step_impl(context: Any, text: str) -> None:
    """
    Checks if the specified text is present within the item results table's body,
    ignoring the header row.

    Args:
        context (Any): The behave context.
        text (str): The text to search for within the table body rows.
    """
    # Target the tbody within the div containing the item results table
    table_body_selector = "#shopcart_find_results tbody"
    # Wait for the table body to be present and check for text within it
    try:
        WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, table_body_selector), text
            )
        )
        found = True
    except TimeoutException:
        found = False

    assert (
        found
    ), f"'{text}' was not found within the table body '{table_body_selector}'"


@then('I should not see "{text}" in the item results table')
def step_impl(context: Any, text: str) -> None:
    """
    Checks if the specified text is NOT present within the item results table's body,
    ignoring the header row.

    Args:
        context (Any): The behave context.
        text (str): The text to search for within the table body rows.
    """
    # Target the tbody within the div containing the item results table
    table_body_selector = "#shopcart_find_results tbody"
    try:
        # Ensure the table body is present first (or wait for it)
        table_body = WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, table_body_selector)
            )
        )
        # Check the text within the located table body
        assert (
            text not in table_body.text
        ), f"'{text}' was unexpectedly found within the table body '{table_body_selector}'"
    except TimeoutException:
        # If the table body never appears, the text isn't in it.
        assert True
    except NoSuchElementException:
        # If the element is not found after waiting (should be caught by TimeoutException mostly)
        assert True


@when('I set the ID to "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    # Get a list of all the shopcarts
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    response_data = context.resp.json()
    if response_data and len(response_data) > 0:
        text_string = str(response_data[0]["id"])
    element_id = "shopcart_id"
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "-") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{number}" shopcarts in the results')
def step_impl(context: Any, number: str) -> None:
    """
    Counts the number of shopcart data rows (ignoring the header) in the results table.

    Args:
        context (Any): The behave context.
        number (str): The expected number of shopcarts as a string.
    """
    # Target rows within the tbody element of the all_shopcarts table
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#all_shopcarts tbody tr")
    row_count = len(rows)
    expected_count = int(number)
    assert (
        row_count == expected_count
    ), f"Expected {expected_count} shopcarts, but found {row_count}"


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    # Uncomment next line to take a screenshot of the web page for debugging
    # save_screenshot(context, message)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='shopcart_name'
# We can then lowercase the name and prefix with shopcart_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@when('I clear the "{element_name}" field')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()

@then('the "{element_name}" field should not be "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    actual_value = element.get_attribute("value")
    assert actual_value != text_string, f"Expected {element_name} not to be '{text_string}', but it was."

@then('the "{element_name}" field should not be empty')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    actual_value = element.get_attribute("value")
    assert actual_value != "", f"Expected {element_name} not to be empty, but it was."