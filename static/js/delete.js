$(document).ready(function(){
	$('#delete').click(function(){
		alert("error");
		var name = $(this).attr('form');
		
		$.ajax({
			url: '/deletePhoto',
			data: name,
			type: 'POST',
			success: function(response){
				alert(response);
		},
			error: function(error){
				console.log(error);
			}
		});
	});
});