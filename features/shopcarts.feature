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
        Then I should see "Shopcart Demo RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Retrieve a Shopcart
        When I visit the "Home Page"
        And I set the ID to "1"
        And I press the "Search" button
        Then I should see "Milk" in the "name" field

    Scenario: Delete a Shopcart
        When I visit the "Home Page"
        And I set the ID to "1"
        And I press the "Delete" button
        Then I should see the message "Shopcart has been Deleted!"
    
    Scenario: Fill the item form
        When I visit the "Home Page"
        And I set the ID to "1"
        And I press the "Search" button
        Then I should see "2" in the "Quantity" field

    Scenario: Clear items
        When I visit the "Home Page"
        And I set the ID to "1"
        And I press the "Search" button
        Then I should see "Milk" in the "name" field
        When I press the "clear" button
        Then the "name" field should be empty

  #### New


    Scenario: Create a new shopcart, and verify retrieval
        When I visit the "Home Page"
        And I set the "shopcart_customer_id" to "301"
        And I set the "shopcart_id" to "1"
        And I press the "create shopcart" button
        Then I should see the message "Success"
        And I press the "search" button
        Then I should see "301" in the "shopcart_customer_id" field
        And the item results table should be empty

    Scenario: Add an item to an existing shopcart and copy its generated ID
        # Uses background shopcart 1
        When I visit the "Home Page"
        And I set the "shopcart_id" to "1"
        And I press the "Search" button
        # Fill the item form, providing a dummy/placeholder item_id
        And I set the "item_id" to "999"
        And I set the "name" to "Yogurt"
        And I set the "quantity" to "6"
        And I set the "price" to "1.10"
        And I set the "description" to "Strawberry yogurt cups"
        And I press the "create item" button
        Then I should see the message "Success: Item added to Shopcart 1!"
        # JS updated the item_id field with the server-generated ID
        Then the "item_id" field should not be "999"
        And the "item_id" field should not be empty
        And I should see "Yogurt" in the "name" field # Verify other fields remain
        When I copy the "item_id" field # Copy the generated Item ID for potential later use

    Scenario: Create a shopcart, add an item to it using generated IDs
        Given the server is running
        When I visit the "Home Page"
        And I set the "shopcart_customer_id" to "402"
        And I press the "Create New Shopcart" button
        Then I should see the message "Success - New shopcart created."
        # Capture the generated Shopcart ID
        When I copy the "shopcart_id" field

        # Now add an item to this new cart
        # Ensure the copied shopcart ID is in the field (it should be after creation)
        And I paste the "shopcart_id" field # Paste just to be sure

        # Fill item details with a dummy item ID
        And I set the "item_id" to "777"
        And I set the "name" to "Cereal"
        And I set the "quantity" to "1"
        And I set the "price" to "4.25"
        And I set the "description" to "Breakfast cereal box"
        And I press the "Create item" button
        Then I should see the message containing "Success: Item added to Shopcart"

        # Verification: Search using the copied shopcart ID and check item
        When I clear the "shopcart_id" field
        And I paste the "shopcart_id" field # Paste the generated shopcart ID again for search
        And I press the "Search" button
        Then I should see "402" in the "shopcart_customer_id" field
        And I should see "Cereal" in the item results table
        And I should see "1" in the item results table # Quantity
        And I should see "4.25" in the item results table
        # Check the item form is populated with the added item (including generated ID)
        Then I should see "Cereal" in the "name" field
        And the "item_id" field should not be "777"
        And the "item_id" field should not be empty

    Scenario: Update an item using its generated ID (Requires Add Item scenario first)
        # This scenario conceptually follows the 'Add an item...' scenario
        # Assumes 'Yogurt' was added to cart 1, and its generated ID is in clipboard
        # Pre-condition check (ensure we're starting from the right state)
        Given the shopcart "1" contains an item named "Yogurt" # Needs a step definition for this
        When I visit the "Home Page"
        And I set the "shopcart_id" to "1"
        And I press the "Search" button
        # Need to select the correct item if search populates form with first item only
        # Assuming Yogurt is now the first/only item loaded after adding it
        Then I should see "Yogurt" in the "name" field
        # Paste the Item ID copied from the 'Add Item' scenario if needed
        # Usually, the ID should be in the field if the item is loaded correctly.
        # When I paste the "item_id" field

        # Update the quantity
        When I change the "quantity" to "10"
        And I press the "Update item" button
        Then I should see the message "Success" # Or actual update success message

        # Verification
        When I press the "Search" button # Re-search the shopcart
        Then I should see "10" in the item results table # Verify updated quantity for Yogurt
        And I should see "Yogurt" in the item results table

    # --- Error Handling Scenarios (Unchanged from previous plan) ---

    Scenario: Search for a non-existent shopcart
        When I visit the "Home Page"
        And I set the "shopcart_id" to "9999"
        And I press the "Search" button
        Then I should see the message "Shopcart with id [9999] was not found." # Verify exact error message
        And the item results table should be empty # Or show "No items found"

    Scenario: Attempt to add an item with missing required fields
        Given the following shopcarts
            | id | customer_id |
            | 1  | 1           |
        When I visit the "Home Page"
        And I set the "shopcart_id" to "1"
        And I press the "Search" button
        # Attempt to add item missing 'name'
        And I set the "item_id" to "888"
        And I set the "quantity" to "1"
        And I set the "price" to "1.00"
        And I press the "Create item" button
        Then I should see the message "Item Name, Quantity, Price, and Item ID are required." # Verify exact message