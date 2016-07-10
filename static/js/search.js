$(document).ready(function(){
	$('#btnSearch').click(function(){
		$.ajax({
			url: '/searchPhoto',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				// alert(response)
				var wishObj = JSON.parse(response);
				// var wish = '';
				$('#showImage').empty();
				$.each(wishObj,function(index, value){
					// wish = $(div).clone();
					// $(wish).find('h4').text(value.Title);
					// $(wish).find('p').text(value.Description);
          var $row = $(
            '<div class="col-md-4">' + 
            '<a href= "http://res.cloudinary.com/coopals/image/upload/' + value.url +'"  class="thumbnail">' +
            '<img src="http://res.cloudinary.com/coopals/image/upload/' + value.url + '" alt="Pulpit Rock" style="width:180px;height:150px">' +
            '<a><button id = "delete"' + 'form = "' + value.url + '" >delete</button></a>' +  '<span style="padding-left:250px"> <a><button>verify</button></a>' +
            '</a>' + 
            '</div>' 
            );
					$('#showImage').append($row);
				});
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});