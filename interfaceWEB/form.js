function campos(){
    var e = document.getElementById("formControlSelect1");
    var modo = e.options[e.selectedIndex].value;

    if(modo == 0){
        $("#minutos").attr("disabled", "disabled").val("");
        $("#time").attr("disabled", "disabled").val("");
        $("#umi_min").attr("disabled", "disabled").val("");
        $("#umi_max").attr("disabled", "disabled").val("");
        $("#temp_min").attr("disabled", "disabled").val("");
        $("#temp_max").attr("disabled", "disabled").val("");
        $("#cadastrar").attr("disabled", "disabled");
    }
    else if(modo == 1){
        // enable
        $("#minutos").removeAttr("disabled");
        $("#time").removeAttr("disabled");
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#umi_min").attr("disabled", "disabled").val("");
        $("#umi_max").attr("disabled", "disabled").val("");
        $("#temp_min").attr("disabled", "disabled").val("");
        $("#temp_max").attr("disabled", "disabled").val("");
    }
    else if(modo == 2){
        // enable
        $("#umi_min").removeAttr("disabled");
        $("#umi_max").removeAttr("disabled");
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#minutos").attr("disabled", "disabled").val("");
        $("#time").attr("disabled", "disabled").val("");
        $("#temp_min").attr("disabled", "disabled").val("");
        $("#temp_max").attr("disabled", "disabled").val("");
    }
    else if(modo == 3){
        // enable
        $("#umi_min").removeAttr("disabled");
        $("#minutos").removeAttr("disabled");
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#time").attr("disabled", "disabled").val("");
        $("#umi_max").attr("disabled", "disabled").val("");
        $("#temp_min").attr("disabled", "disabled").val("");
        $("#temp_max").attr("disabled", "disabled").val("");
    }
    else if(modo == 4){
        // enable
        $("#temp_min").removeAttr("disabled");
        $("#temp_max").removeAttr("disabled");
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#minutos").attr("disabled", "disabled").val("");
        $("#time").attr("disabled", "disabled").val("");
        $("#umi_min").attr("disabled", "disabled").val("");
        $("#umi_max").attr("disabled", "disabled").val("");
    }
    else if(modo == 5){
        // enable
        $("#minutos").removeAttr("disabled");
        $("#temp_max").removeAttr("disabled");
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#time").attr("disabled", "disabled").val("");
        $("#umi_min").attr("disabled", "disabled").val("");
        $("#umi_max").attr("disabled", "disabled").val("");
        $("#temp_min").attr("disabled", "disabled").val("");
    }
    else if(modo == 6){
        // enable
        $("#temp_min").removeAttr("disabled");
        $("#temp_max").removeAttr("disabled");
        $("#umi_min").removeAttr("disabled");
        $("#umi_max").removeAttr("disabled");
        $("#cadastrar").removeAttr("disabled");

        // disabled
        $("#minutos").attr("disabled", "disabled").val("");
        $("#time").attr("disabled", "disabled").val("");
    }
}