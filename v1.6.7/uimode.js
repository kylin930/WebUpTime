document.addEventListener('DOMContentLoaded', function () {
    let qhButton = document.getElementById('qh');
    let icon = document.getElementById('icon');
    let isdark = localStorage.getItem('dark') || 'no';
    function dark() {
        isdark=localStorage.getItem('dark') || 'no';
        if (isdark == 'yes') {
            icon.innerHTML = "brightness_2";
            mdui.snackbar({
                message: '已切换深色模式',
                position: 'right-bottom',
            });
            document.body.classList.add("mdui-theme-layout-dark");
        }
        if (isdark == 'no') {
            icon.innerHTML = "brightness_low";
            if (document.body.classList.contains("mdui-theme-layout-dark")) {
                mdui.snackbar({
                message: '已切换浅色模式',
                position: 'right-bottom',
                });
                document.body.classList.remove("mdui-theme-layout-dark");
            }
        }
    }
    dark();
    qhButton.addEventListener('click', function () {
        if (isdark == 'no') {
            isdark='yes';
        } else {
            isdark='no';
        }
        localStorage.setItem('dark', isdark);
        dark();
    });
})
