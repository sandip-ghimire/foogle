(function($){

    var loginViewModel = {logindata:{type: ko.observable('')}}

    $('.loginbtn').click(function () {
        var username = $.trim($('#uname').val());
        var pwd = $.trim($('#pass').val());
        var data = {username: username, password: pwd};

        var loginHandler = $fgl.handlePost('/login', data);
        loginHandler.on('postSuccess', function(resp){
            if (resp == "success") {
                window.location.replace(window.location.href);
            } else {
                $('.loginfailed').css('display', 'block');
            }
        });
        loginHandler.on('postFail', function(xhr, status, error){
            console.log(error);
            $('.loginfailed').css('display', 'block');
        });
    });


    $('.txtbox').on('keypress', function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            $('.loginbtn').click();
        }
    });

    ko.applyBindings(loginViewModel);

})(jQuery);
