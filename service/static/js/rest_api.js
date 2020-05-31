$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    var $api_key = "c38e5e9781dd46cb8eba2299c363bfe7";

    // Updates the form with data from the response
    function update_form_data(res) { //response object
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_category").val(res.category);
        $("#product_price").val(res.price);
        $("#product_stock").val(res.stock);
        $("#product_description").val(res.description);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_name").val("");
        $("#product_category").val("");
        $("#product_price").val("");
        $("#product_stock").val("");
        $("#product_description").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#product_name").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();
        var stock = $("#product_stock").val();
        var description = $("#product_description").val();
        var data = {
            "name": name,
            "category": category,
            "price": price,
            "stock": stock,
            "description" : description
        };

        var headers = {
            'X-Api-Key': $api_key
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/products",
            headers: headers,
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
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();
        var name = $("#product_name").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();
        var stock = $("#product_stock").val();
        var description = $("#product_description").val();

        var data = {
            "name": name,
            "category": category,
            "price": price,
            "stock": stock,
            "description": description
        };

        var headers = {
            'X-Api-Key': $api_key
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/products/" + product_id,
                headers: headers,
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
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/products/" + product_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();

        var headers = {
            'X-Api-Key': $api_key
        };

        var ajax = $.ajax({
            type: "DELETE",
            url: "/products/" + product_id,
            headers: headers,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#product_name").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();

        var queryString = ""

        if (name) {
            queryString += '?name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += '?category=' + category
            }
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            }
            else {
                queryString += '?price=' + price
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/products" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#res_data").empty();
            var header = '<tr>'
            header += '<th class="col-md-1">ID</th>'
            header += '<th class="col-md-3">Name</th>'
            header += '<th class="col-md-3">Category</th>'
            header += '<th class="col-md-2">Price</th>'
            header += '<th class="col-md-2">Stock</th>'
            header += '<th class="col-md-4">Description</th></tr>'
            $("#res_data").append(header);
            var firstProduct = "";
            for(var i = 0; i < res.length; i++) {
                var product = res[i];
                var row = '<tr><td class="col-md-1">'+product.id+'</td><td class="col-md-3">'+product.name+'</td><td class="col-md-3">'+product.category+'</td><td class="col-md-2">'+
                product.price+'</td><td class="col-md-2">'+product.stock+'</td><td class="col-md-4">'+product.description+"</td></tr>";
                $("#res_data").append(row);
                if (i == 0) {
                    firstProduct = product;
                }
            }

            // copy the first result to the form
            if (firstProduct != "") {
                update_form_data(firstProduct)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Buy a Product
    // ****************************************

    $("#buy-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "PUT",
            url: "/products/" + product_id + "/buy",
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

})
