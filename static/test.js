$(document).ready(function ($) {
        $('#tabs').tab();
        $('.dropdown-toggle').dropdown();
        $('.dropdown input, .dropdown label').click(function(e) {
    e.stopPropagation();
        });

        $('.signup').validate({
            rules: {
                nombre: "required",
                apellido: "required",
                password: {
                    required: true,
                    minlength: 5
                     },
                confirm_password: {
                    minlength: 5,
                    equalTo: "#password"
                },
                email: {
                    required: true,
                    email: true
                },
            },
            messages: {
                nombre: "Please enter your firstname",
                apellido: "Please enter your lastname",
                password: {
                    required: "Please provide a password",
                    minlength: "Your password must be at least 5 characters long"
                },
                confirm_password: {
                    equalTo: "Please enter the same password as above"
                },
                email: "Please enter a valid email address",
            }
         });

        $('.login').validate({
            rules: {
                password: {
                    required: true,
                     },
                email: {
                    required: true,
                    email: true
                },
            },
            messages: {
                password: {
                    required: "Please provide a password",
                },
                email: "Please enter a valid email address",
            }
         });

        


        $(".signup").submit(function(e){
            e.preventDefault();
            args = {
                "email":$(this).find('[name="email"]').val(),
                "branch": $(this).find('[name="branch"]').val(),
                '_xsrf' : getCookie("_xsrf"),
                }
            console.log(args); 

            $.ajax({
                url:"/validate",
                type:"POST",
                data: $.param(args),
                success: function(data){
                    if (data == "1"){
                        try{   
                            if (window.location.pathname == "/personas")
                            {
                                $.form('/signup', {
                                    "email":$(".signup").find('[name="email"]').val(),
                                    "branch": $(".signup").find('[name="branch"]').val(),
                                    '_xsrf' : getCookie("_xsrf"),
                                    "password":$(".signup").find('[name="password"]').val(),
                                    "nombre": $(".signup").find('[name="nombre"]').val(),
                                    "apellido":$(".signup").find('[name="apellido"]').val()
                                    }).submit();
                            }
                            else {

                                $.form('/signup', {
                                    "email":$(".signup").find('[name="email"]').val(),
                                    "branch": $(".signup").find('[name="branch"]').val(),
                                    '_xsrf' : getCookie("_xsrf"),
                                    "password":$(".signup").find('[name="password"]').val(),
                                    "nombre": $(".signup").find('[name="nombre"]').val(),
                                    "description":$(".signup").find('[name="description"]').val()
                                    }).submit();

                            }
                        }
                        catch (err){
                            console.log("Error")

                        }
                       
                    }
                    else {
                        console.log(0);
                        $(".signup").append("<p>Error. Email ya utilizado o invalido </p>");

                    } 
                }
            });
        })
       
 
    	if (window.location.pathname == "/cbox")
		{
			updater.poll();
            
		}

        if (window.location.pathname == "/box")
        {   
            var a = $(".beneficio").html();
            var b = "Reservado";
            var i = 0;

                
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

        if (window.location.pathname == "/companies")
        {   
            var a = $(".seguir").html();
            var b = "Siguiendo";

            var i = 0;

                
            $(".seguir").click(function(){
                i++;
                
                if (i%2 != 0) {
                    $(this).html(b);
                    
                    
                    var beneficio = {
                        'company_id':$(this).parent().find("[name='company_id']").val(),
                        '_xsrf' : getCookie("_xsrf"),
                        'action':'seguir'
                    }
                    

                    $.ajax({
                        url: '/follow',
                        type: "POST",
                        data : beneficio,
                        success: function(){
                            console.log(beneficio);
                        }});


                    
                }else {
                    $(this).html(a);
                    var beneficio = {

                        'company_id':$(this).parent().find("[name='company_id']").val(),
                        '_xsrf' : getCookie("_xsrf"),
                        'action': 'borrar'
                    }
                    $.ajax({
                        url: "/follow",
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


jQuery(function($) { $.extend({
    form: function(url, data, method) {
        if (method == null) method = 'POST';
        if (data == null) data = {};

        var form = $('<form>').attr({
            method: method,
            action: url
         }).css({
            display: 'none'
         });

        var addData = function(name, data) {
            if ($.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    var value = data[i];
                    addData(name + '[]', value);
                }
            } else if (typeof data === 'object') {
                for (var key in data) {
                    if (data.hasOwnProperty(key)) {
                        addData(name + '[' + key + ']', data[key]);
                    }
                }
            } else if (data != null) {
                form.append($('<input>').attr({
                  type: 'hidden',
                  name: String(name),
                  value: String(data)
                }));
            }
        };

        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                addData(key, data[key]);
            }
        }

        return form.appendTo('body');
    }
}); });