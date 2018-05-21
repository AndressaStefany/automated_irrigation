
// Starter JavaScript for disabling form submissions if there are invalid fields
(function() {
    'use strict';
    window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
        form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
        }, false);
    });
    }, false);
})();


function campos(){
    var e = document.getElementById("formControlSelect1");
    var modo = e.options[e.selectedIndex].value;

    if(modo == 0){
        $("#minutos").attr("disabled", "disabled").val("").prop("required",false);
        $("#time").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_max").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_max").attr("disabled", "disabled").val("").prop("required",false);
        $("#cadastrar").attr("disabled", "disabled");
    }
    else if(modo == 1){
        // enable
        $("#minutos").removeAttr("disabled").prop("required",true);
        $("#time").removeAttr("disabled").prop("required",true);
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#umi_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_max").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_max").attr("disabled", "disabled").val("").prop("required",false);
    }
    else if(modo == 2){
        // enable
        $("#umi_min").removeAttr("disabled").prop("required",true);
        $("#umi_max").removeAttr("disabled").prop("required",true);
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#minutos").attr("disabled", "disabled").val("").prop("required",false);
        $("#time").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_max").attr("disabled", "disabled").val("").prop("required",false);
    }
    else if(modo == 3){
        // enable
        $("#umi_min").removeAttr("disabled").prop("required",true);
        $("#minutos").removeAttr("disabled").prop("required",true);
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#time").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_max").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_max").attr("disabled", "disabled").val("").prop("required",false);
    }
    else if(modo == 4){
        // enable
        $("#temp_min").removeAttr("disabled").prop("required",true);
        $("#temp_max").removeAttr("disabled").prop("required",true);
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#minutos").attr("disabled", "disabled").val("").prop("required",false);
        $("#time").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_max").attr("disabled", "disabled").val("").prop("required",false);
    }
    else if(modo == 5){
        // enable
        $("#minutos").removeAttr("disabled").prop("required",true);
        $("#temp_max").removeAttr("disabled").prop("required",true);
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#time").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_min").attr("disabled", "disabled").val("").prop("required",false);
        $("#umi_max").attr("disabled", "disabled").val("").prop("required",false);
        $("#temp_min").attr("disabled", "disabled").val("").prop("required",false);
    }
    else if(modo == 6){
        // enable
        $("#temp_min").removeAttr("disabled").prop("required",true);
        $("#temp_max").removeAttr("disabled").prop("required",true);
        $("#umi_min").removeAttr("disabled").prop("required",true);
        $("#umi_max").removeAttr("disabled").prop("required",true);
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#minutos").attr("disabled", "disabled").val("").prop("required",false);
        $("#time").attr("disabled", "disabled").val("").prop("required",false);
    }
}