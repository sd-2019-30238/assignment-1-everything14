function activateUser(id){
    $.ajax({
        url: id + '/activateUser',
        type: 'POST',
        async: true,
        success: function(res) {
            alert("User " + id + " activated succesfully!");
            location.reload();
        }
    })
}