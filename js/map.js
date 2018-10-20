let cityName = window.location.pathname.split('/')[2];

$.get('/city/'+cityName, (data) => {
    data = JSON.parse(data);
    $('.main_img').attr('src', data.bingLink);
    $('#percentage').text(data.info.percent);
    $('#profit').text(data.info.profit);
    $('#treeArea').text(data.info.treeArea);
    $('#treeAmount').text(data.info.treeCount);
});

$('.mask_rgz').attr("src", "/mask_rgz/"+cityName);
$('.mask_mgz').attr("src", "/mask_mgz/"+cityName);
$('.mask_pgz').attr("src", "/mask_pgz/"+cityName);
$('.mask_vpgz').attr("src", "/mask_vpgz/"+cityName);

let list = data.map(function(i) { 
    if (i && i.name)
        return i["name"].toString(); }
);
let test = new Awesomplete(document.getElementById("cityField"))
test.filter = function (text, input) {
	return text.toLowerCase().startsWith(input.toLowerCase());
}
test.list = list;

$('form').submit(function(e){
    let city = $('input').val().toUpperCase();
    if (list.indexOf(city)!==-1) window.location.replace("/map/"+city.toLowerCase());
    e.preventDefault();
})

$('#cityField').prop('placeholder', cityName.toUpperCase().replace('%20', ' '));

$('input[type=range]').on('change mousemove', (e) => {
    $('.mask_'+e.target.id).css('opacity', parseFloat(e.target.value)/100);
});