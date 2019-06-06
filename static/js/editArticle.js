function editArticle(id){
    $.ajax({
        url: id + '/editArticleForm',
        type: 'GET',
        async: true,
        success: function(res) {
        }
    })
}