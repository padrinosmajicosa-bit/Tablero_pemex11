function actualizarHora(){

    let hoy = new Date();

    let opciones = {

        weekday:'long',
        year:'numeric',
        month:'long',
        day:'numeric',

        hour:'2-digit',
        minute:'2-digit',
        second:'2-digit'

    };

    document.getElementById("fechaHora").innerHTML =
        hoy.toLocaleDateString('es-MX',opciones);

}

setInterval(actualizarHora,1000);

actualizarHora();