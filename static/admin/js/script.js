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
                                window.setTimeout(function () { }, 2000);
                            }
                        }
                    },
                    error: function (data) {
                        Swal.hideLoading();

                        var title = "An error occurred";
                        var message =
                            "An error occurred. Please try again later.";
                        Swal.fire(title, message, "error");
                    },
                });
            }, 100);
        }
    });
});

$(document).ready(function () {

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


    $('.approve-product').click(function () {
        var csrfToken = getCSRFToken(); // Get the CSRF token
        if (!csrfToken) {
            console.error("CSRF token not found.");
            return;
        }
        var itemId = $(this).data("item-id");
        console.log(itemId, 'id');
    
        var confirmButtonText = "Yes";
        var confirmButtonColor = "#DD6B55";
    
        Swal.fire({
            title: "Confirm Product Approve",
            text: "Are you sure you want approve?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: confirmButtonText,
            confirmButtonColor: confirmButtonColor,
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/customadmin/order/orders-cancelled-or-returned/approve/${itemId}/`,
                    method: "POST",
                    dataType: "json",
                    data: {
                        csrfmiddlewaretoken: csrfToken,
                    },
                    success: function (data) {
                        if (data.status == 'success') {
                            const statusCompleted = document.querySelector('#status-completed');
                            const statusPending = document.querySelector('#status-pending');
                            if (data.status == 'completed') {
                                statusCompleted.textContent = data.order_status
                            }
                            else{
                                statusPending.textContent = data.order_status
                            }

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
                                icon: data.status,
                                title: data.title,
                            });
    
                        } else {
                            console.log("else");
                        }
                    },
                    error: function () {
                        console.log("error");
                    },
                });
            }
        });
    })

})