Feature: The shopcarts service back-end
    As a customer
    I need a RESTful shopcarts service
    So that I can manage my shopping cart and its items

    Background:
        Given the following shopcarts
            | id | customer_id |
            | 1  | 1           |
            | 2  | 2           |
        And the following items in shopcarts
            | item_id | name   | quantity | price | description       |
            | 1       | Milk   | 2        | 3.50  | Fresh milk carton |
            | 2       | Bread  | 1        | 2.00  | Whole grain loaf  |
            | 3       | Apples | 5        | 1.20  | Red apples pack   |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Shopcarts REST API Service" in the title
        And I should not see "404 Not Found"

    Scenario: Delete a Shopcart
        Given a shopcart exists with "id" of "1"
        When I delete the shopcart with "id" of "1"
        Then I should see the message "Success"
        And the shopcart with "id" of "1" should no longer exist
    '''
    Scenario: Create a Shopcart
        When I visit the "Home Page"
        And I set the "Customer ID" to "3"
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "Customer ID" field should be empty

    Scenario: Retrieve a Shopcart
        Given a shopcart exists with "Customer ID" of "1"
        When I retrieve the shopcart with "Id" of "1"
        Then I should see the "Customer ID" as "1"
        And I should see the "Time Atc" as "2023-10-01T10:00Z"

    Scenario: Update a Shopcart
        Given a shopcart exists with "Customer ID" of "1"
        When I update the "Customer ID" to "10" for the shopcart with "Id" of "1"
        Then I should see the message "Success"
        And I should see the "Customer ID" as "10"



    Scenario: List all Shopcarts
        When I retrieve all shopcarts
        Then I should see "2" shopcarts in the results
        And I should see a shopcart with "Customer ID" of "1"
        And I should see a shopcart with "Customer ID" of "2"

    Scenario: Add an Item to a Shopcart
        Given a shopcart exists with "Customer ID" of "1"
        When I add an item with "Name" as "Milk", "Quantity" as "2", and "Price" as "3.50" to the shopcart with "Id" of "1"
        Then I should see the message "Success"
        And I should see the item "Milk" in the shopcart with "Id" of "1"

    Scenario: Retrieve an Item from a Shopcart
        Given a shopcart exists with "Customer ID" of "1" and contains an item "Milk"
        When I retrieve the item "Milk" from the shopcart with "Id" of "1"
        Then I should see the "Name" as "Milk"
        And I should see the "Quantity" as "2"
        And I should see the "Price" as "3.50"

    Scenario: Update an Item in a Shopcart
        Given a shopcart exists with "Customer ID" of "1" and contains an item "Milk"
        When I update the "Quantity" to "5" for the item "Milk" in the shopcart with "Id" of "1"
        Then I should see the message "Success"
        And I should see the "Quantity" as "5" for the item "Milk"

    Scenario: Delete an Item from a Shopcart
        Given a shopcart exists with "Customer ID" of "1" and contains an item "Milk"
        When I delete the item "Milk" from the shopcart with "Id" of "1"
        Then I should see the message "Success"
        And the item "Milk" should no longer exist in the shopcart with "Id" of "1"

    Scenario: Clear all Items in a Shopcart
        Given a shopcart exists with "Customer ID" of "1" and contains multiple items
        When I clear all items from the shopcart with "Id" of "1"
        Then I should see the message "Success"
        And the shopcart with "Id" of "1" should have no items

'''