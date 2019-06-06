
$(function() {    
    $('#btnLeaveMessage').click(function() {
 
        $.ajax({
            url: '/leaveMessage',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                var x = document.getElementById("success");
                x.style.display = "block";
                document.getElementById('success-msg').innerHTML = response;
                $.ajax({
                    url: '/index'
                });
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});