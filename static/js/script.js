$(document).on("submit", "form.ajax", function (e) {
    e.preventDefault();
    var $this = $(this);

    document.onkeydown = function (evt) {
        return false;
    };

    var url = $this.attr("action");
    var method = $this.attr("method");
    var isReload = $this.hasClass("reload");
    var isRedirect = $this.hasClass("redirect");
    var noLoader = $this.hasClass("no-loader");
    var noPopup = $this.hasClass("no-popup");

    if (!noLoader) {
        Swal.showLoading();
    }

    jQuery.ajax({
        type: method,
        url: url,
        dataType: "json",
        data: new FormData(this),
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            console.log("success");
            if (!noLoader) {
                Swal.hideLoading();
            }

            var message = data["message"];
            var status = data["status"];
            var title = data["title"];
            var redirect = data["redirect"];
            var redirect_url = data["redirect_url"];
            var stable = data["stable"];

            if (status == "success") {
                if (title) {
                    title = title;
                } else {
                    title = "Success";
                }

                function doAfter() {
                    if (stable != "yes") {
                        console.log(isRedirect);
                        console.log(redirect);
                        if (isRedirect && redirect === "yes") {
                            window.location.href = redirect_url;
                        }
                        if (isReload) {
                            window.location.reload();
                        }
                    }
                }

                if (noPopup) {
                    doAfter();
                } else {
                    Swal.fire({
                        icon: status,
                        title: title,
                        html: message,
                    }).then((result) => {
                        console.log(result.isConfirmed);
                        if (result.isConfirmed) {
                            doAfter();
                        }
                    });
                }
                document.onkeydown = function (evt) {
                    return true;
                };
            } else {
                if (title) {
                    title = title;
                } else {
                    title = "An Error Occurred";
                }

                Swal.fire(title, message, "error");

                if (stable != "true") {
                    window.setTimeout(function () {}, 2000);
                }
                document.onkeydown = function (evt) {
                    return true;
                };
            }
        },
        error: function (data) {
            console.log("err");
            Swal.hideLoading();

            var title = "An error occurred";
            var message = "An error occurred. Please try again later.";
            document.onkeydown = function (evt) {
                return true;
            };
            Swal.fire(title, message, "error");
        },
    });
});

$(document).on("click", ".action-button", function (e) {
    e.preventDefault();
    $this = $(this);
    var text = $this.attr("data-text");
    var type = "warning";
    var confirmButtonText = "Yes";
    var confirmButtonColor = "#DD6B55";
    var url = $this.attr("href");
    var title = $this.attr("data-title");
    if (!title) {
        title = "Are you sure?";
    }
    var isReload = $this.hasClass("reload");
    var isRedirect = $this.hasClass("redirect");
    var noResponsePopup = $this.hasClass("no-response-popup");

    Swal.fire({
        title: title,
        text: text,
        icon: type,
        showCancelButton: true,
        confirmButtonText: confirmButtonText,
        confirmButtonColor: confirmButtonColor,
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.showLoading();

            window.setTimeout(function () {
                jQuery.ajax({
                    type: "GET",
                    url: url,
                    dataType: "json",
                    success: function (data) {
                        var message = data["message"];
                        var status = data["status"];
                        var redirect = data["redirect"];
                        var redirect_url = data["redirect_url"];
                        var stable = data["stable"];
                        var title = data["title"];

                        Swal.hideLoading();

                        if (status == "success") {
                            if (title) {
                                title = title;
                            } else {
                                title = "Success";
                            }
                            if (!noResponsePopup) {
                                Swal.fire({
                                    icon: "success",
                                    title: title,
                                    text: message,
                                    type: "success",
                                }).then((result) => {
                                    if (stable != "yes") {
                                        if (isRedirect && redirect == "yes") {
                                            window.location.href = redirect_url;
                                        }
                                        if (isReload) {
                                            window.location.reload();
                                        }
                                    }
                                });
                            }
                        } else {
                            if (title) {
                                title = title;
                            } else {
                                title = "An Error Occurred";
                            }

                            Swal.fire(title, message, "error");

                            if (stable != "true") {
                                window.setTimeout(function () {}, 2000);
                            }
                        }
                    },
                    error: function (data) {
                        Swal.hideLoading();

                        var title = "An error occurred";
                        var message = "An error occurred. Please try again later.";
                        Swal.fire(title, message, "error");
                    },
                });
            }, 100);
        }
    });
});

$(document).ready(function () {
    // Function to get the CSRF token from the page's cookies
    function getCSRFToken() {
        var csrfToken = null;
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                csrfToken = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
        return csrfToken;
    }

    // Attach click event handlers to the increment and decrement buttons
    $(".increment-quantity").click(function () {
        var productId = $(this).data("product-id");
        updateQuantity(productId, "increment");
    });

    $(".decrement-quantity").click(function () {
        var productId = $(this).data("product-id");
        updateQuantity(productId, "decrement");
    });

    // Function to send AJAX request to update_product_quantity
    function updateQuantity(productId, action) {
        var csrfToken = getCSRFToken(); // Get the CSRF token
        if (!csrfToken) {
            console.error("CSRF token not found.");
            return;
        }

        console.log(action);
        // Include the CSRF token in the headers of the AJAX request
        $.ajax({
            url: "/shop/product/quantity/" + productId + "/",
            method: "POST", // Use POST method for CSRF protection
            data: {
                action: action,
                csrfmiddlewaretoken: csrfToken, // Include CSRF token here
            },
            dataType: "json",
            success: function (data) {
                if (data.exceeded) {
                    Swal.fire({
                        icon: data.status,
                        title: data.title,
                        text: data.message,
                    });
                } else if (data.under_limit) {
                    var confirmButtonText = "Yes";
                    var confirmButtonColor = "#DD6B55";

                    Swal.fire({
                        title: data.title,
                        text: data.text,
                        icon: data.type,
                        showCancelButton: true,
                        confirmButtonText: confirmButtonText,
                        confirmButtonColor: confirmButtonColor,
                    }).then((result) => {
                        if (result.isConfirmed) {
                            clickedButton.closest("tr").remove();
                        }
                    });
                } else {
                    console.log(data.total_amount);
                    const totalPriceOfEachProduct = document.querySelector(`#total_price_of_product_${productId}`);
                    totalPriceOfEachProduct.textContent = "₹" + data.amount;

                    const subTotal = document.querySelector(`#sub_total_price`);
                    subTotal.textContent = "₹" + data.total_amount;

                    const total = document.querySelector(`#total_price`);
                    total.textContent = "₹" + data.total_amount;

                    $("#quantity-" + productId).val(data.qty);
                }
            },
            error: function (err) {
                console.log("error", err);
            },
        });
    }

    $(".remove-product").click(function (event) {
        event.preventDefault(); // Prevent the default form submission

        var csrfToken = getCSRFToken(); // Get the CSRF token
        if (!csrfToken) {
            console.error("CSRF token not found.");
            return;
        }

        var productId = $(this).data("product-id");
        var clickedButton = $(this);

        $.ajax({
            url: "/shop/user/cart/remove/" + productId + "/",
            method: "POST",
            dataType: "json",
            data: {
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (data) {
                console.log("success");
                if (data.success) {
                    console.log("if");
                    var confirmButtonText = "Yes";
                    var confirmButtonColor = "#DD6B55";

                    Swal.fire({
                        title: data.title,
                        text: data.text,
                        icon: data.type,
                        showCancelButton: true,
                        confirmButtonText: confirmButtonText,
                        confirmButtonColor: confirmButtonColor,
                    }).then((result) => {
                        if (result.isConfirmed) {
                            clickedButton.closest("tr").remove();
                            const cartCounts = document.querySelectorAll(".cart-count");

                            cartCounts.forEach(function (cartCount) {
                                cartCount.textContent = data.cart_count;
                            });
                        }
                    });
                } else {
                    console.log("else");
                }
            },
            error: function () {
                console.log("error");
            },
        });
    });

    $(".add-to-wishlist").click(function (event) {
        event.preventDefault();
        var $heartIcon = $(this).find("i");

        // Toggle the classes
        // if ($heartIcon.hasClass("far")) {
        //     $heartIcon.removeClass("far").addClass("fas");
        // } else {
        //     $heartIcon.removeClass("fas").addClass("far");
        // }

        var productId = $(this).data("product-id");
        addToWishlist(productId);
    });

    function addToWishlist(productId) {
        $.ajax({
            url: "/shop/user/wishlist/add/" + productId + "/",
            dataType: "json",
            success: function (data) {
                if (data) {
                    console.log("Added to wishlist");
                    const Toast = Swal.mixin({
                        toast: true,
                        position: "top-end",
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true,
                        didOpen: (toast) => {
                            toast.addEventListener("mouseenter", Swal.stopTimer);
                            toast.addEventListener("mouseleave", Swal.resumeTimer);
                        },
                    });

                    Toast.fire({
                        icon: "success",
                        title: "Added to wishlist",
                    });
                }
            },
            error: function () {
                console.log("Error adding to wishlist");
            },
        });
    }

    $(".remove-from-wishlist").click(function (event) {
        event.preventDefault(); // Prevent the default link behavior

        var csrfToken = getCSRFToken(); // Get the CSRF token
        if (!csrfToken) {
            console.error("CSRF token not found.");
            return;
        }
        var productId = $(this).data("product-id");

        $.ajax({
            url: `/shop/user/wishlist/remove/${productId}/`,
            method: "POST", // You can use POST or other appropriate method
            dataType: "json",
            data: {
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (data) {
                if (data) {
                    console.log(data.count, "count");
                    if (data.count < 1) {
                        window.location.href = "/shop/all/";
                    }
                    $(`.product-item-${productId}`).remove();

                    const Toast = Swal.mixin({
                        toast: true,
                        position: "top-end",
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true,
                        didOpen: (toast) => {
                            toast.addEventListener("mouseenter", Swal.stopTimer);
                            toast.addEventListener("mouseleave", Swal.resumeTimer);
                        },
                    });

                    Toast.fire({
                        icon: "warning",
                        title: "Removed From Wishlist",
                    });
                } else {
                }
            },
            error: function () {
                // alert('An error occurred while processing your request.');
            },
        });
    });

    $(".add-to-cart").click(function (event) {
        event.preventDefault(); // Prevent the default link behavior

        var csrfToken = getCSRFToken(); // Get the CSRF token
        if (!csrfToken) {
            console.error("CSRF token not found.");
            return;
        }
        var productId = $(this).data("product-id");

        $.ajax({
            url: `/shop/user/cart/add/${productId}/`,
            method: "POST", // You can use POST or other appropriate method
            dataType: "json",
            data: {
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (data) {
                if (data.success) {
                    console.log("cart");
                    const cartCounts = document.querySelectorAll(".cart-count");

                    cartCounts.forEach(function (cartCount) {
                        cartCount.textContent = data.cart_count;
                    });
                    
                    const Toast = Swal.mixin({
                        toast: true,
                        position: "top-end",
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true,
                        didOpen: (toast) => {
                            toast.addEventListener("mouseenter", Swal.stopTimer);
                            toast.addEventListener("mouseleave", Swal.resumeTimer);
                        },
                    });

                    Toast.fire({
                        icon: "success",
                        title: "Added to cart",
                    });
                } else {
                }
            },
            error: function () {
                // alert('An error occurred while processing your request.');
            },
        });
    });
});
