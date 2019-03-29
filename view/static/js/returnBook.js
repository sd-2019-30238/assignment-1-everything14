function returnBook(id){
    $.ajax({
        url: id + '/returnBook',
        type: 'POST',
        async: true,
        success: function(res) {
            alert("Returned succesfully!");
            location.reload();
        }
    })
}