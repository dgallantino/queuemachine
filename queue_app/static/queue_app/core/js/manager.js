(function($){
	$.fn.list_booth = function(){
		var $this = $(this);
		url = $this.attr('booth_url');
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
	
	$.fn.as_booking_form_modal = function(){
		$(this).on('click',function(event){
			event.preventDefault();
			var popup_window = window.open($(this).attr('href'),"_blank","width=1000,height=1000'");
			
		});
	};
	
	$.fn.as_finish_button = function(selector){
		if (selector === undefined){
			const err = new Error("blody hell mate, selector argument is mandatory, don't let it empty you stupid wanker");
			throw err;
		}
		$(this).on('click',selector,function(event){
			event.preventDefault();
			var $this = $(this);
			var url = $this.attr('href');
			var session_booth = $this.attr('session_booth');
			if (!session_booth){
				var error_message = "System Err:\n";
        		error_message += "[404] : Please choose your counter / desk first";
        		window.alert(error_message);
        		return false;
			}
			var form_data = "call_flag=on&counter_booth="+session_booth;
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
        	    $this.closest('tr').remove();	    
        	});
		});
	};
	
	//request the most updated queue list
	$.fn.as_queue_list = function(){
		$.each(this,function(idx,dom_obj){
			var queue_url = $(dom_obj).attr('queues_url');
			var loading_html =	'<tr><td class ="text-center" colspan="5">';
			loading_html += '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>';
			loading_html += '<span class="sr-only">Loading...</span>';
			loading_html += '</td></tr>';
			$(dom_obj).html(loading_html);
			$.ajax({
				url:queue_url,
				type:'GET',
				dataType:'html',
				contentType: 'application/x-www-form-urlencoded',				
			})
			.fail(function(xhr){
				window.alert(xhr.status.toString());
			})
			.done(function(response){
				$(dom_obj).html(response);
			});
		});
		return false;
	};
}(jQuery));