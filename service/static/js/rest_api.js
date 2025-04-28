$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************


    // Create a clipboard variable to store copied values
    let clipboard = "";

    // Function to copy shopcart ID to clipboard
    function copy_shopcart_id() {
        clipboard = $("#shopcart_id").val();
        console.log("Clipboard contains: " + clipboard);
    }

    // Function to paste shopcart ID from clipboard
    function paste_shopcart_id() {
        $("#shopcart_id").val(clipboard);
    }

    // Function to display the flash message
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }
    
// Updates the form with data from the response
    function update_form_data(res) {
        $("#item_id").val(res.id);
        $("#name").val(res.name);
        $("#quantity").val(res.quantity);
        $("#price").val(res.price);
        $("#description").val(res.description);
        $("#shopcart_customer_id").val(res.shopcart_customer_id);
    }

    // Function to clear the form
    function clear_form_data() {
        $("#shopcart_id").val("");
        $("#item_id").val("");
        $("#name").val("");
        $("#quantity").val("");
        $("#price").val("");
        $("#description").val("");
        $("#shopcart_find_results").empty();
        $("#shopcart_find_customer tbody").empty();
    }

    // Function to update form with the first item from search results
    function update_form_with_first_item(items) {
        if (items && items.length > 0) {
            let item = items[0];
            $("#item_id").val(item.id || "");
            $("#name").val(item.name || "");
            $("#quantity").val(item.quantity || "");
            $("#price").val(item.price || "");
            $("#description").val(item.description || "");
        }
    }

    // ****************************************
    // Copy Shopcart ID
    // ****************************************
    
    $("#copy-id-btn").click(function() {
        copy_shopcart_id();
        flash_message("Shopcart ID copied to clipboard!");
    });

    // ****************************************
    // Paste Shopcart ID
    // ****************************************
    
    $("#paste-id-btn").click(function() {
        paste_shopcart_id();
        flash_message("Shopcart ID pasted from clipboard!");
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        $("#shopcart_customer_id").val("");
        $("#item_id").val("");
        $("#name").val("");
        $("#quantity").val("");
        $("#price").val("");
        $("#description").val("");
        $("#flash_message").empty();
        $("#shopcart_find_results").empty();
        $("#shopcart_find_customer tbody").empty();
        clear_form_data();
    });
    
    // ****************************************
    // Create a Shopcart - UPDATED
    // ****************************************

    $("#create-btn").click(function () {

        let id = $("#id").val();
        let customer_id = $("#shopcart_customer_id").val();
 

        let data = {
            "id": id,
            "customer_id": customer_id,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            // Store the ID in clipboard automatically after creation
            clipboard = res.id.toString();
            console.log("Shopcart ID copied to clipboard: " + clipboard);
            flash_message("Success - ID copied to clipboard");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });



    // ****************************************
    // Delete a Shopcart - UPDATED
    // ****************************************

    $("#delete-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
    
    // ****************************************
    // Create a New Shopcart
    // ****************************************

    $("#create-shopcart-btn").click(function () {
        // Get customer_id from input field
        let customer_id = $("#shopcart_customer_id").val();
        
        // Validate Customer ID
        if (!customer_id) {
            flash_message("Customer ID is required to create a shopcart.");
            return;
        }
        
        // Clear the flash message area
        $("#flash_message").empty();
        
        // Get shopcart_id from input field
        let shopcart_id_from_input = $("#shopcart_id").val();
        
        // Prepare base payload
        let data = {
            "customer_id": customer_id
        };
        // Add shopcart_id from input if it has a value
        if (shopcart_id_from_input) {
            // Assuming the backend deserialize might look for 'id'
            data.id = shopcart_id_from_input; 
        }
        
        
        // Perform AJAX POST request
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });
        
        // Handle successful response
        ajax.done(function(res) {
            // Store ID in clipboard
            clipboard = res.id.toString();
            console.log("Shopcart ID copied to clipboard: " + clipboard);
            
            // Update shopcart_id field with the new ID
            $("#shopcart_id").val(res.id);
            
            // Clear item form fields
            $("#item_id").val("");
            $("#name").val("");
            $("#quantity").val("");
            $("#price").val("");
            $("#description").val("");

            $("#list-btn").click();
            
            flash_message("Success - New shopcart created. ID copied to clipboard");
        });
        
        // Handle error response
        ajax.fail(function(res) {
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Create/Add an Item to a Shopcart
    // ****************************************
    $("#create-item-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val(); // Get Shopcart ID from the main search field

        // Validate Shopcart ID
        if (!shopcart_id) {
            flash_message("Shopcart ID is required to add an item.");
            return; // Exit if no shopcart ID
        }

        // Get item details from the Item Management form
        let name = $("#name").val();
        let quantity_str = $("#quantity").val();
        let price_str = $("#price").val();
        let description = $("#description").val();
        let id = $("#item_id").val();

        // Validate required item fields
        if (!name || !quantity_str || !price_str || !id) {
             flash_message("Item Name, Quantity, Price, and Item ID are required.");
             return; // Exit if required fields are missing
        }

        // Prepare JSON payload - Parse quantity and price
        let data = {
            "id": id,
            "name": name,
            "quantity": parseInt(quantity_str), // Convert to integer
            "price": parseFloat(price_str),     // Convert to float
            "description": description
        };

        // Construct the API endpoint URL
        let url = `/shopcarts/${shopcart_id}/items`;

        // Clear flash message and perform AJAX POST
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "POST",
            url: url,
            contentType: "application/json",
            data: JSON.stringify(data) // Send data as JSON string
        });

        // Handle Success
        ajax.done(function(res){
            flash_message("Success: Item added to Shopcart " + shopcart_id + "!");
            // Update the form fields with response data
            $("#item_id").val(res.id);
            $("#name").val(res.name);
            $("#quantity").val(res.quantity);
            $("#price").val(res.price);
            $("#description").val(res.description);
            
            // Store the item response data
            let itemData = {
                id: res.id,
                name: res.name,
                quantity: res.quantity,
                price: res.price,
                description: res.description
            };
            
            // Refresh the item list in the UI
            $("#search-btn").click();
            
            // Restore form fields after search completes
            setTimeout(function() {
                $("#item_id").val(itemData.id);
                $("#name").val(itemData.name);
                $("#quantity").val(itemData.quantity);
                $("#price").val(itemData.price);
                $("#description").val(itemData.description);
            }, 500); // Small delay to ensure search completes
        });

        // Handle Failure
        ajax.fail(function(res){
             // Display error message from server response or a generic one
             flash_message(res.responseJSON ? res.responseJSON.message : "Error adding item.");
        });
    });

    // ****************************************
    // Search for all Shopcarts - UPDATED
    // ****************************************

    $("#search-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        // Clear previous results and flash message
        $("#shopcart_find_results").empty();
        $("#flash_message").empty();

        // Check if shopcart_id is provided
        if (!shopcart_id) {
            flash_message("Please enter a Shopcart ID to search.");
            return;
        }

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`, // Use the specific shopcart ID
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            // Check if the response is a single shopcart object with items and customer_id
            if (res && typeof res === 'object' && res.hasOwnProperty('customer_id') && Array.isArray(res.items)) {
                // Update the customer_id field from the response
                $("#shopcart_customer_id").val(res.customer_id || "");

                // Populate Items table (existing logic)
                $("#shopcart_find_results").empty(); // Clear previous results if any
                let table = '<table class="table table-striped table-hover">'
                table += '<thead><tr>'
                table += '<th class="col-md-1">Item ID</th>'
                table += '<th class="col-md-2">Name</th>'
                table += '<th class="col-md-1">Quantity</th>'
                table += '<th class="col-md-1">Price</th>'
                table += '<th class="col-md-7">Description</th>'
                table += '</tr></thead><tbody>'


                if (res.items.length > 0) {
                    for (let j = 0; j < res.items.length; j++) {
                        let item = res.items[j];
                        table += `<tr id="row_${j}">
                            <td>${item.id || ""}</td>
                            <td>${item.name || ""}</td>
                            <td>${item.quantity || ""}</td>
                            <td>${item.price || ""}</td>
                            <td>${item.description || ""}</td>
                        </tr>`;
                    }
                    
                    // Update form with first item's data
                    update_form_with_first_item(res.items);
                } else {
                    // Handle case where the shopcart has no items
                    table += `<tr><td colspan="5">No items found in this shopcart.</td></tr>`;
                }

                table += '</tbody></table>';
                $("#shopcart_find_results").html(table);
                flash_message("Success");
            } else {
                // Handle unexpected response format
                $("#shopcart_find_results").html('<p>Could not display items. Unexpected response format.</p>');
                flash_message("Error: Unexpected response format.");
            }
        });

        ajax.fail(function(res){
            $("#shopcart_find_results").empty(); // Clear results on failure
            flash_message(res.responseJSON ? res.responseJSON.message : "An error occurred");
        });

    });


    



    // ****************************************
    // LIST ALL SHOPCARTS
    // ****************************************

    $("#list-btn").click(function () {
        $("#existing_carts tbody").empty(); // Clear previous results
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/shopcarts",
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            if (Array.isArray(res)) {
                let tableBody = $("#existing_carts tbody");
                
                if (res.length > 0) {
                    for (let i = 0; i < res.length; i++) {
                        let row = `<tr><td>${res[i].id}</td><td>${res[i].customer_id}</td></tr>`;
                        tableBody.append(row);
                    }
                    flash_message("Success");
                } else {
                    tableBody.append('<tr><td colspan="2">No shopcarts found</td></tr>');
                    flash_message(res.responseJSON ? res.responseJSON.message : "No shopcarts found");
                }
            } else {
                flash_message(res.responseJSON ? res.responseJSON.message : "Unexpected response format");
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON ? res.responseJSON.message : "Error listing shopcarts");
        });
    });


    // ****************************************
    // UPDATE AN ITEM IN A SHOPCART
    // ****************************************
    $("#update-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();
        let item_id = $("#item_id").val();
        
        // Validate required IDs
        if (!shopcart_id || !item_id) {
            flash_message("Both Shopcart ID and Item ID are required for updating.");
            return; // Exit if required IDs are missing
        }
        
        // Get item details from the form
        let name = $("#name").val();
        let quantity_str = $("#quantity").val();
        let price_str = $("#price").val();
        let description = $("#description").val();
        
        // Validate required item fields
        if (!name || !quantity_str || !price_str) {
            flash_message("Item Name, Quantity, and Price are required fields.");
            return; // Exit if required fields are missing
        }
        
        // Prepare JSON payload
        let data = {
            "id": item_id,
            "name": name,
            "quantity": parseInt(quantity_str), // Convert to integer
            "price": parseFloat(price_str),     // Convert to float
            "description": description
        };
        
        // Clear flash message and perform AJAX PUT request
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "PUT",
            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });
        
        // Handle Success
        ajax.done(function(res){
            update_form_data(res);
            flash_message("Item successfully updated!");
            
            // Refresh the item list to show updated data
            $("#search-btn").click();
        });
        
        // Handle Failure
        ajax.fail(function(res){
            flash_message(res.responseJSON ? res.responseJSON.message : "Error updating item.");
        });
    });

});
