function borrowBook(id){
    $.ajax({
        url: id + '/borrowBook',
        type: 'POST',
        async: true,
        success: function(res) {
            alert("Book borrowed succesfully!");
            
        }
    })
}