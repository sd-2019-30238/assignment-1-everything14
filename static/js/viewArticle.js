function viewArticle(id){
    $.ajax({
        url: id + '/viewArticle',
        type: 'GET',
        async: true,
        success: function(res) {
        }
    })
}