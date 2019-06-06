function deleteArticle(id){
    $.ajax({
        url: id + '/deleteArticle',
        type: 'DELETE',
        async: true,
        success: function(res) {
            alert("Deleted succesfully!");
            location.reload();
        }
    })
}