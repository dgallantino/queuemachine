function PrintTicket(data) {
    var contents = data;
    var frame1 = document.createElement('iframe');
    frame1.name = "frame1";
    frame1.style.position = "absolute";
    frame1.style.top = "-1000000px";
    document.body.appendChild(frame1);
    var frameDoc = frame1.contentWindow ? frame1.contentWindow : frame1.contentDocument.document ? frame1.contentDocument.document : frame1.contentDocument;
    frameDoc.document.open();
    frameDoc.document.write('<html>');
    frameDoc.document.write(contents);
    frameDoc.document.write('</html>');
    frameDoc.document.close();
    setTimeout(function () {
        window.frames["frame1"].focus();
        window.frames["frame1"].print();
        document.body.removeChild(frame1);
    }, 500);
    return false;
}

//as jquery plugin
(function( $ ) {
	
	//not sure why
	print_ticket = function( data ) {
    	var contents = data;
        var frame1 = document.createElement('iframe');
        frame1.name = "frame1";
        frame1.style.position = "absolute";
        frame1.style.top = "-1000000px";
        document.body.appendChild(frame1);
        var frameDoc = frame1.contentWindow ? frame1.contentWindow : frame1.contentDocument.document ? frame1.contentDocument.document : frame1.contentDocument;
        frameDoc.document.open();
        frameDoc.document.write('<html>');
        frameDoc.document.write(contents);
        frameDoc.document.write('</html>');
        frameDoc.document.close();
        setTimeout(function () {
            window.frames["frame1"].focus();
            window.frames["frame1"].print();
            document.body.removeChild(frame1);
        }, 500);
        return false;
    };
	 
    $.fn.get_queues = function() {
    	var $this=$(this);
    	var latest_queue_id = $this.find('.list:last-child').attr('queue_id')
    	var url=$this.attr('queues_url')+(latest_queue_id?latest_queue_id:"");
    	$.ajax({
    		url : url,
    		type : "GET",
    		dataType: 'html',
    	})
    	.fail(function(xhr){
    		var error_message = "AJAX Err:\n";
    		error_message += "["+xhr.status.toString()+"] : ";
    		error_message += xhr.statusText;
    		window.alert(error_message);
    	})
    	.done(function(data){
    		$this.append(data);
    	});
 
    };
    
    $.fn.as_print_handler = function(selector){
		if (selector === undefined){
			const err = new Error("blody hell mate, selector argument is mandatory, don't let it empty you stupid wanker");
			throw err;
		}
    	$(this).on('click',selector,function(event){
			event.preventDefault();
    		var $this = $(this);
        	var url = $this.attr('href');
        	var service = $this.attr('service_id')?'&service='+$this.attr('service_id'):'';
        	var form_data = "print_flag=on"+service;
        	console.log(form_data);
        	$.ajax({
        		url : url,
        		type : "POST",
        		dataType: 'html',
        		contentType: 'application/x-www-form-urlencoded',
        		data:form_data,
        		
        	})
        	.fail(function(xhr){
        		var error_message = "AJAX Err:\n";
        		error_message += "["+xhr.status.toString()+"] : ";
        		error_message += xhr.statusText;
        		window.alert(error_message);	
        	})
        	.done(function(data){
        		print_ticket(data);
        	    if(!service) $this.parent('.list').remove();	    
        	});
    	});
    	//prevent default action
    	return false;
    };
    
    $.fn.as_print_new_queue_handler = function(selector){
    	$(this).on('submit',selector, function(event){
    		if (selector || false){
				event.preventDefault();	
	    		var asd = $.param($(this).serializeArray());
	    		console.log(asd);
	    		var url = $(this).attr('action');
	    		$.ajax({
	    			url : url,
	    			type : "POST",
	    			dataType: 'html',
	    			contentType: 'application/x-www-form-urlencoded',
	    			data:$(this).serialize(),
	    		})
	    		.fail(function(xhr){
	    			var error_message = "AJAX Err:\n";
	    			error_message += "["+xhr.status.toString()+"] : ";
	    			error_message += xhr.statusText;
	    			window.alert(error_message);
	    		})
	    		.done(function(data){
	    			print_ticket(data);	    
	    		});
    		}
    		return false
    	});
    };
    
 
}( jQuery ));