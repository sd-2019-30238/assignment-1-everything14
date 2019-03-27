function deleteBook(id){
    $.ajax({
        url: id + '/deleteBook',
        type: 'POST',
        async: true,
        success: function(res) {
            alert("Deleted succesfully!");
            location.reload();
        }
    })
}