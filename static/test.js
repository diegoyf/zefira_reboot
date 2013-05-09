$(document).ready(function ($) {
        $('#tabs').tab();
        $('.dropdown-toggle').dropdown();
        $('.dropdown input, .dropdown label').click(function(e) {
    e.stopPropagation();

  	});
    	if (window.location.pathname == "/cbox")
		{
			waitForMsg();
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
                        'title' : $(this).parent().find("[name='benefit_title']").text() ,
                        'description' : $(this).parent().find("[name='benefit_desc']").text(),
                        '_xsrf' : getCookie("_xsrf"),
                        'action' : 'reserve'
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

function waitForMsg(){
        
        document.company_id = $("#company_id").val(); 
        $.ajax({
            type: "GET",
            url: "/activity",

            async: true, /* If set to non-async, browser shows page as "Loading.."*/
            cache: false,
            data: {"company_id" : document.company_id},
            
            timeout:50000, /* Timeout in ms */

            success: function(data){ /* called when request to barge.php completes */
                addmsg("new", data); /* Add response to a .msg div (with the "new" class)*/
                setTimeout(
                    waitForMsg, /* Request next message */
                    10000 /* ..after 1 seconds */
                );
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                addmsg("error", textStatus + " (" + errorThrown + ")");
                setTimeout(
                    waitForMsg, /* Try again after.. */
                    10000); /* milliseconds (15seconds) */
            }
        });
    };


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
