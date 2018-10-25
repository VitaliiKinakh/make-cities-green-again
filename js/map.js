let cityName = window.location.pathname.split('/')[2];

let a,b,c,d,q;

setTimeout(()=>{
    $('.mask_rgz').attr("src", "/rgz/"+cityName);
    $('.mask_pgz').attr("src", "/pgz/"+cityName);
    $('.mask_vpgz').attr("src", "/vpgz/"+cityName);
    $('.mask_mgz').attr("src", "/mgz/"+cityName);
    a = $('.pannable-image:eq(0)').ImageViewer();
    b = $('.pannable-image:eq(1)').ImageViewer();
    c = $('.pannable-image:eq(2)').ImageViewer();
    d = $('.pannable-image:eq(3)').ImageViewer();
    q = $('.pannable-image:eq(4)').ImageViewer();
    $.get('/city/'+cityName, (data) => {
        data = JSON.parse(data);
        $('#percentage').text((data.info.percent*100).toFixed(2));
        $('#profit').text(data.info.profit.toFixed(2));
        $('#treeArea').text(data.info.treeArea);
        $('#treeAmount').text(data.info.treeCount);
    });
}, 15000);

$('.main_img').attr("src", "/landsat/"+cityName);

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

let imgArr = []

$('body').on('mapZoom', (e, par1, x, y) => {
    b.data('ImageViewer').zoom(par1, {x, y})
    c.data('ImageViewer').zoom(par1, {x, y})
    d.data('ImageViewer').zoom(par1, {x, y})
    q.data('ImageViewer').zoom(par1, {x, y})
});


$('#cityField').prop('placeholder', cityName.toUpperCase().replace('%20', ' '));

let arr = ['rgz', 'mgz', 'pgz', 'vpgz'];

$('input[type=range]').on('change mousemove', (e) => {
    let containers = $('.iv-container')
    let images = $('.iv-large-image')
    $(images[arr.indexOf(e.target.id)+1]).css('opacity', parseFloat(e.target.value)/100);
    $(containers[arr.indexOf(e.target.id)+1]).css('opacity', parseFloat(e.target.value)/100);
});