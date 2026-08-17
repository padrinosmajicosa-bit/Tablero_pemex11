// ===============================
// GRAFICA DE BARRAS
// ===============================

const barras = document.getElementById("graficaProyectos");

new Chart(barras,{

    type:"bar",

    data:{

        labels:["RCN","SR","Backlog","RCN Activo"],

        datasets:[{

            label:"Cantidad",

            data:[120,95,40,80],

            borderWidth:1

        }]

    },

    options:{

        responsive:true,

        plugins:{

            legend:{
                display:false
            }

        }

    }

});

// ===============================
// GRAFICA CIRCULAR
// ===============================

const circular=document.getElementById("graficaCircular");

new Chart(circular,{

    type:"doughnut",

    data:{

        labels:["RCN","SR","Backlog","Activo"],

        datasets:[{

            data:[120,95,40,80]

        }]

    },

    options:{

        responsive:true

    }

});