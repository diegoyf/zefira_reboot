$(document).ready(function ($) {
        $('#tabs').tab();
        $('.dropdown-toggle').dropdown();
        $('.dropdown input, .dropdown label').click(function(e) {
    e.stopPropagation();

       
  	});
    	if (window.location.pathname == "/cbox")
		{
			updater.poll();
            
		}

        if (window.location.pathname == "/box")
        {   
            var a = "Reservar";
            var b = "Reservado";
            var i = 0;

            $(".beneficio").html(a);    
            $(".beneficio").click(function(){
                i++;
                if (i%2 != 0) {

                    $(this).html(b);
                    
                    var beneficio = {
                        'benefit_id' : $(this).parent().find("[name='benefit_id']").val(),
                        '_xsrf' : getCookie("_xsrf"),
                        'action' : 'reserve',
                        'company_id':$(this).parent().find("[name='company_id']").val()
                    }
                    

                    $.ajax({
                        url: '/reserve',
                        type: "POST",
                        data : beneficio,
                        success: function(){
                            console.log(beneficio);
                        }});


                    
                }else {
                    $(this).html(a);
                    var beneficio = {
                        'benefit_id' : $(this).parent().find("[name='benefit_id']").val(),
                        'company_id':$(this).parent().find("[name='company_id']").val(),
                        '_xsrf' : getCookie("_xsrf"),
                        'action':'delete'
                    }
                    $.ajax({
                        url: "/reserve",
                        type: "POST",
                        data:  beneficio,
                        success : function(){
                            console.log(beneficio)
                        }
                    })
                    
                }
                });
                
        }
    });




function addmsg(type, msg){
        /* Simple helper to add a div.
        type is the name of a CSS class (old/new/error).
        msg is the contents of the div */
        var msg2 = $.parseJSON(msg);
        $("#messages").append(
            "<div class='msg "+ type +"'>"+ msg2[0].title +"</div>"
        );

    }


var updater = {
    errorSleepTime: 500,
    cursor : null,

    poll:function(){
        var args = {"_xsrf": getCookie("_xsrf")};
        if(updater.cursor) args.cursor = updater.cursor;
        args.company_id = $("#company_id").val();
         
        
        $.ajax({
            url: "/activity",
            type: "GET",
            dataType: "text",
            data: $.param(args),
            success: updater.onSuccess,
            error: updater.onError,

        });

    },
    onSuccess: function(response) {
        
        updater.errorSleepTime = 500;
        window.setTimeout(updater.poll,  0);
    },

    onError: function(response) {
        updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newMessages: function(response) {
        if (!response.messages) return;
        updater.cursor = response.cursor;
        var messages = response.messages;
        updater.cursor = messages[messages.length - 1].id;
        console.log(messages.length, "new messages, cursor:", updater.cursor);
        for (var i = 0; i < messages.length; i++) {
            updater.showMessage(messages[i]);
        }
    },

    showMessage: function(message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        var node = $(message.html);
        node.hide();
        $("#inbox").append(node);
        node.slideDown();
    }

};
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
