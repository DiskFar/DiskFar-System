// Estilo para os links ativos da navbar
document.querySelectorAll('.nav-link').forEach(function(elemento){ 
    if(elemento.pathname.split('/')[1] == window.location.pathname.split('/')[1] ){
        elemento.classList.add('atual')
    }
    else{
        elemento.classList.remove('atual')
    }})

// Esconde as mensagens após um tempo
setTimeout(function() {
    let message = document.querySelector('.messages');
    if (message !== undefined && message !== null){
        message.style.display = 'none'
    }
}, 3000)

// Renderiza as imagens antes de salvar
$('#id_imagem').change(function(){
    elemento = $('#id_imagem')[0]
    if (elemento.files && elemento.files[0]) {
        var src = URL.createObjectURL(elemento.files[0])
        $('#image').attr('src', src)
        $('#image').removeClass('d-none')
        $('#image_').addClass('d-none')
    }
    else{
        $('#image_').removeClass('d-none')
        $('#image').addClass('d-none')
    }
})

function resetar_imagem(){
    $("#id_imagem").val(null);
    $("#id_imagem").trigger("change")
}

// Renderiza os comprovantes antes de salvar
$('#id_comprovante').change(function(){
    elemento = $('#id_comprovante')[0]
    if (elemento.files && elemento.files[0]) {
        var src = URL.createObjectURL(elemento.files[0])
        $('#comprovante').attr('src', src)
        $('#comprovante').removeClass('d-none')
        $('#comprovante_').addClass('d-none')
    }
    else{
        $('#comprovante_').removeClass('d-none')
        $('#comprovante').addClass('d-none')
    }
})

function resetar_comprovante(){
    $("#id_comprovante").val(null);
    $("#id_comprovante").trigger("change")
}

// Exibe criação de uma nova categoria
$(".toggle-control").click(function(){
	$("#form_toggle").toggleClass('d-none d-flex');
});

// Exibe o filtro do relatório de pedidos
$(".filtro-control").click(function(){
	$("#form_filtro").toggleClass('d-none');
    $(".btn-csv-pedido").toggleClass('d-none');
});

// Preenche o endereço de entrega
$("#id_cep").blur(function(){
    var cep = this.value.replace(/[^0-9]/, "")
    if(/[a-z]/i.test(cep)){alert(`O CEP: ${cep} informado não é válido!`); this.value = ""}
    else {
        var url = `https://viacep.com.br/ws/${cep}/json/`
        $.get(url, function(data){
            if(data.erro){
                alert(`CEP: ${cep} não encontrado!`)
                $("#id_endereco").val("")
                $("#id_bairro").val("")
                $("#id_cep").val("")}
            else {
                $("#id_endereco").val(data.logradouro)
                $("#id_bairro").val(data.bairro)}
    })}
});

elemento = document.querySelector("select[name=produto]")
elemento.onchange = function (){ 
    codigo = elemento.value ? elemento.value : 0
    $.get({
        type: "GET",
        url: "/api/produto/" + codigo, 
    success: function(data) {
        if (data) {
            document.querySelector("span#qtd").innerText = data["qtd"];
            document.querySelector("#id_quantidade").max = data["qtd"];
        } else {
            document.querySelector("span#qtd").innerText = 0;
        }
    },
    error:function(e){
        alert("something wrong"+ e) // this will alert an error
        }
    });
}

function getProduto(){
    alert("Evento acionado!")
    //$.post("/api/get_produto", {"produto": 1} ,alert("request ajax aqui"));
}

function contato() {
    alert("Mensagem enviada, retornaremos o mais breve possível.");
};

// Copia link de pagamento para área de transferência
function copyLinkClipboard(){
    var url = $(document.getElementById('mercadopago')).attr('href');
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val(url).select();
    document.execCommand("copy");
    $temp.remove();
    alert("Link copiado para a área de transferência!");
};