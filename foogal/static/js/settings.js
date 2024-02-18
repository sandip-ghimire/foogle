(function($){
    var SettingModel = Backbone.Model.extend({
        urlRoot: "/handle_settings",
        post: function(data) {
            $fgl.handlePost(this.urlRoot, data, this.onPostSuccess, this.onPostFail);
        },
        load: function() {
            $fgl.handleGet(this.urlRoot, this.onGetSuccess, this.onGetFail);
        },
    });
    var settingObj =  new SettingModel()
    SettingModel.prototype.onGetSuccess = function (resp) {
        if (!$.isEmptyObject(resp)){
            settingObj.set(resp);
            settingObj.trigger('dataFetched');
        }
    }


    var LinkModel = $fgl.BaseModel.extend({
        urlRoot: "/links",
        post: function(data) {
            $fgl.handlePost(this.urlRoot, data, this.onPostSuccess, this.onPostFail);
        },
    });
    var linkObj =  new LinkModel()
    linkObj.on('change', function(){
        this.save();
    });

    if ($fgl.loggedIn) {
        settingObj.load();
        linkObj.fetch({
            success: function(resp){
                $('#url-list-txt').text(linkObj.get('urls'));
            }
        });
    }

    Dropzone.autoDiscover = false;
    var fileList = new Array;
    var dropZone = $(".dropzone").dropzone({
        url: '/upload',
        uploadMultiple: true,
        width: 300,
        height: 200,
        addRemoveLinks: true,
        acceptedFiles: ".txt,.pdf",
        dictInvalidFileType: "Invalidformat",
        headers: {"X-CSRFToken": $fgl.getCookie("csrftoken")},

        init: function () {
            var myDropZone = this;
            this.on("processing", function (file) {
            });

            this.on("complete", function (file) {
                $(".dz-progress").css('opacity', '0');
                $(".dz-remove").text('Remove');
            });

            this.on("addedfile", function(file){
                var ext = file.name.split('.').pop();

                if (ext == "pdf") {
                    $(file.previewElement).find(".dz-image img").attr("src", "/static/images/pdf.png");
                } else if (ext.indexOf("txt") != -1) {
                    $(file.previewElement).find(".dz-image img").attr("src", "/static/images/txt.png");
                }
            });

         },
        removedfile: function(file) {
            file.previewElement.remove();
            $(".dz-message").remove();
            var fileRemoveHandler = $fgl.handlePost('/remove_files', {filename:file.name});
            fileRemoveHandler.on('postSuccess', function(resp){
            })
            fileRemoveHandler.on('postFail', function(xhr, status, error){
            })
        },
        error: function (file, response) {
            if (response=='Invalidformat'){
                file.previewElement.remove();
            }
        },
        success: function (file, response) {
        },

    });

    $('.addurlbtn').click(function () {

        var existingUrls = $('#url-list-txt').text();
        var newUrl = $('#url-item').val();
        $('#url-item').val('');

        if (newUrl.trim()) {
            if (existingUrls){
                $('#url-list-txt').text(existingUrls + ',' + newUrl);
            }else {
                $('#url-list-txt').text(newUrl);
            }
            linkObj.set('setting', $fgl.configObj.get('defaultset'));
            linkObj.set('urls', $('#url-list-txt').text())
        }
    });


    $('#url-item').on('keypress', function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            $('.addurlbtn').click();
        }
    });

    $('#settingModal').on('shown.bs.modal', function (e) {
    	$('.errordiv').css('display', 'none');
    	$('.errordivsmall').css('display', 'none');
    })
    $('#settingModal').on('hidden.bs.modal', function (e) {
    	var previewElements = document.querySelectorAll(".dz-preview");
    })
    settingObj.on('dataFetched', function(){
        resp = settingObj.toJSON()
        if (resp.status == 'success'){
            filenames = resp.filenames;
            if (filenames.length > 0){
                _.each(filenames, function(filedetail){
                    var file = {name: filedetail.file_name, size: filedetail.file_size}
                    Dropzone.forElement("#fodz").emit('addedfile', file);
                    Dropzone.forElement("#fodz").emit('complete', file);
                });
            }
        }

    })

})(jQuery);



