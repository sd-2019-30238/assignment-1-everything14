$(function() {    
    $('#btnAddBook').click(function() {
        $.ajax({
            url: '/addBook',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});