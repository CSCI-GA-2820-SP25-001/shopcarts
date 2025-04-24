$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S - UPDATED
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.customer_id || "");
            }

    // Clears all form fields
   function clear_form_data() {
        $("#customer_id").val("");
    }


    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#shopcart_name").val();
        let category = $("#shopcart_category").val();
        let available = $("#shopcart_available").val() == "true";
        let gender = $("#shopcart_gender").val();
        let birthday = $("#shopcart_birthday").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "gender": gender,
            "birthday": birthday
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();
        let name = $("#shopcart_name").val();
        let category = $("#shopcart_category").val();
        let available = $("#shopcart_available").val() == "true";
        let gender = $("#shopcart_gender").val();
        let birthday = $("#shopcart_birthday").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "gender": gender,
            "birthday": birthday
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${shopcart_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart - UPDATED
    // ****************************************

    $("#retrieve-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();
        
        $("#flash_message").empty();
        console.log("Retrieving shopcart with ID:", shopcart_id);
        
        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            console.log("Success retrieving shopcart:", res);
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            clear_form_data();
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
    // Clear the form - UPDATED
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        $("#customer_id").val('');
        $("#item_id").val('');
        $("#name").val('');
        $("#quantity").val('');
        $("#price").val('');
        $("#description").val('');
        $("#flash_message").empty();
        clear_form_data();
    });

    // ****************************************
    // Search for all Shopcarts - UPDATED
    // ****************************************

    $("#search-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        // Clear previous results and flash message
        $("#shopcart_find_results").empty();
        $("#shopcart_find_customer tbody").empty(); // Clear customer table too
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
                // Populate Customer ID table
                $("#shopcart_find_customer tbody").empty(); // Clear previous customer ID
                let customerTableBody = $("#shopcart_find_customer tbody");
                let customerRow = `<tr><td>${res.customer_id}</td></tr>`;
                customerTableBody.append(customerRow);

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
                $("#shopcart_find_customer tbody").empty(); // Clear customer table on error too
                flash_message("Error: Unexpected response format.");
            }
        });

        ajax.fail(function(res){
            $("#shopcart_find_results").empty(); // Clear results on failure
            $("#shopcart_find_customer tbody").empty(); // Clear customer table on failure
            flash_message(res.responseJSON ? res.responseJSON.message : "An error occurred");
        });

    });

})
