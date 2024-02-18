var $fgl = (function($){
    var BaseModel = Backbone.Model.extend({
        sync: function(method, model, options) {
            options = options || {};
            if (method === 'create') {
                options.headers = options.headers || {};
                options.headers["X-CSRFToken"] = getCookie("csrftoken");
                options.headers['Content-Type'] =  'application/json';
            }
            return Backbone.sync(method, model, options);
        }
    });
    function handlePost(url, data, successCallback=undefined, failCallback=undefined) {
        var postHandler = _.extend({}, Backbone.Events);
        if (typeof data === 'object') {
            data = JSON.stringify(data)
        }
        $.ajax({
                url: url,
                type: "POST",
                contentType: 'application/json',
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                data: data
            }).done(function (resp) {
                if (successCallback){
                    successCallback(resp);
                }
                postHandler.trigger('postSuccess', resp);
            }).fail(function(xhr, status, error) {
                if (failCallback){
                    failCallback(xhr, status, error);
                }
                postHandler.trigger('postFail', xhr, status, error);
            });
        return postHandler
    }

    function handleGet(url, successCallback, failCallback) {
        $.ajax({
                url: url,
                type: "GET",
            }).done(function (resp) {
                successCallback(resp);
            }).fail(function(xhr, status, error) {
                failCallback(xhr, status, error);
            });
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function addScript(srcs) {
      _.each(srcs, function(src){
        var s = document.createElement('script');
        s.setAttribute('src', '/static/js/'+src );
        document.body.appendChild(s);
      })
    }
    // Config Model
    var ConfigModel = BaseModel.extend({
        urlRoot: "/config",
        post: function(data) {
            handlePost(this.urlRoot, data, this.onPostSuccess, this.onPostFail);
        },
    });
    var configObj =  new ConfigModel()
    configObj.on('change', function(){
        configObj.save();
    });

    // UserConfig Model
    var UserConfigModel = BaseModel.extend({
        urlRoot: "/user_config",
    });
    var userConfigObj =  new UserConfigModel()
    userConfigObj.on('change', function(){
        userConfigObj.save();
    });

    var loggedIn = $('#current-user').attr('authenticated') === 'True'
    if (loggedIn){
        userConfigObj.fetch({
            success: function(resp) {
                if (!userConfigObj.has('scope')) {
                    userConfigObj.set('scope', 'internal')
                }
            }
        });
    }

    $(document).ready(function () {

        configObj.fetch({
            success: function(resp) {
                 var wikiTog = configObj.get('wiki_enabled') ? 'on' : 'off';
                 $('#wikiToggle').bootstrapToggle(wikiTog);
            }
        });

        $('.asktxt').focus();
        $('.loader').hide()

        $('.txtbox').focusin(function () {
            $(this).parent().find('.iconbox').css({ "padding-left": "35px" });
            $('.loginfailed').css('display', 'none');

        });
        $('.txtbox').focusout(function () {
            $(this).parent().find('.iconbox').css({ "padding-left": "50px" });
        });

        $('.txtbox').hover(function () {
            $(this).parent().find('.iconbox').css({ "color": "#17a2b8" });
        }, function () {
            $(this).parent().find('.iconbox').css({ "color": "#666666" });
        });
    });
    return{
        BaseModel: BaseModel,
        handleGet: handleGet,
        handlePost: handlePost,
        getCookie: getCookie,
        configObj: configObj,
        userConfigObj: userConfigObj,
        loggedIn: loggedIn
    };
})(jQuery);
