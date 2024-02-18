
(function($){

    var LocalLinkModel = $fgl.BaseModel.extend({
        urlRoot: "/handle_local_links",
        post: function(data) {
            $fgl.handlePost(this.urlRoot, data, this.onPostSuccess, this.onPostFail);
        },
    });
    var llinkObj =  new LocalLinkModel()

    $('.askbtn').click(function () {

        var existingText = $('#result-txt').attr('content');
        var newText = $('.asktxt').val();
        $('.asktxt').val('');

        if (newText.trim()) {
            if (existingText){
                var content = existingText + '<b>' + newText + '</b>' + '<br>'
                $('#result-txt').html(content);
                $('#result-txt').attr('content', content)
            }else {
                $('.splashtext').hide();
                var content = '<b>' + newText + '</b>' + '<br>';
                $('#result-txt').html(content);
                $('#result-txt').attr('content', content);
            }


            var askHandler = $fgl.handlePost('/handle_asks', {ask:newText.trim()});
            $('.loader').show();
            $('.askbtn').prop('disabled', true);
            $('.maintextarea').scrollTop($('.maintextarea').prop("scrollHeight"));

            askHandler.on('postSuccess', function(resp){
                $('.loader').hide();
                $('.askbtn').prop('disabled', false);
                if (resp.status == 'success'){
                    var content = $('#result-txt').attr('content')  + resp.data.response + '<br> <br>'
                    $('#result-txt').html(content);
                    $('#result-txt').attr('content', content)
                } else {
                    var errMsg = '<span style="color:red"> Failed to generate response. </span>';
                    var content = $('#result-txt').attr('content')  + errMsg + '<br> <br>';
                    $('#result-txt').html(content);
                    $('#result-txt').attr('content', content);
                }
                $('.maintextarea').scrollTop($('.maintextarea').prop("scrollHeight"));
            })
            askHandler.on('postFail', function(xhr, status, error){
                $('.loader').hide();
                $('.askbtn').prop('disabled', false);
                console.log(error);
                var errMsg = '<span style="color:red"> Failed to generate response. </span>';
                var content = $('#result-txt').attr('content')  + errMsg + '<br> <br>';
                $('#result-txt').html(content);
                $('#result-txt').attr('content', content);
                $('.maintextarea').scrollTop($('.maintextarea').prop("scrollHeight"));
            })
        }

    });


    $('.asktxt').on('keypress', function (e) {
        if (e.keyCode == 13 && $('.askbtn').prop('disabled') === false) {
            e.preventDefault();
            $('.askbtn').click();
        }
    });


    $('.addlocalurlbtn').click(function () {

        var existingUrls = $('#localurl-list-txt').text();
        var newUrl = $('#localurl-item').val();
        $('#localurl-item').val('');

        if (newUrl.trim()) {
            if (existingUrls){
                $('#localurl-list-txt').text(existingUrls + ',' + newUrl);
            }else {
                $('#localurl-list-txt').text(newUrl);
            }
            llinkObj.set('setting', $fgl.configObj.get('localset'));
            llinkObj.set('urls', $('#localurl-list-txt').text());
            llinkObj.save();
        }


    });

    $('.clearall').click(function () {
        $('#localurl-list-txt').text('');
        $('#localurl-item').val('');
        llinkObj.set('urls', '');
        llinkObj.save();
    });

    $('#linkModal').on('shown.bs.modal', function (e) {
    	$('#localurl-item').focus();
    	var wikiTog = $fgl.configObj.get('wiki_enabled') ? 'on' : 'off';
    	$('#wikiToggle').bootstrapToggle(wikiTog);
    	llinkObj.fetch({
            success: function(resp){
                $('#localurl-list-txt').text(llinkObj.get('urls'));
            }
        });
    })

    $('#wikiToggle').change(function() {
        var togglevalue = $(this).prop('checked');
        if (togglevalue){
            $fgl.configObj.set('wiki_enabled', true);

        }else{
            $fgl.configObj.set('wiki_enabled', false);
        }
    });

    $('#localurl-item').on('keypress', function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            $('.addlocalurlbtn').click();
        }
    });

})(jQuery)
