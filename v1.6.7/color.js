document.addEventListener('DOMContentLoaded', function () {
    var dialog = new mdui.Dialog('#colorPickerDialog');
    var colorPickerButton = document.getElementById('colorPickerButton');
    var primaryColorInput = document.getElementById('primaryColorInput');
    var accentColorInput = document.getElementById('accentColorInput');
    var applyColorButton = document.getElementById('applyColorButton');

    // 定义 MDUI 支持的颜色
    let primaryColors = [
        { name: 'red'},
        { name: 'pink'},
        { name: 'purple'},
        { name: 'deep-purple'},
        { name: 'indigo'},
        { name: 'blue'},
        { name: 'light-blue'},
        { name: 'cyan'},
        { name: 'teal'},
        { name: 'green'},
        { name: 'light-green'},
        { name: 'lime'},
        { name: 'yellow'},
        { name: 'amber'},
        { name: 'orange'},
        { name: 'deep-orange'},
        { name: 'brown'},
        { name: 'grey'},
        { name: 'blue-grey'}
    ];

    let accentColors = [
        { name: 'red'},
        { name: 'pink'},
        { name: 'purple'},
        { name: 'deep-purple'},
        { name: 'indigo'},
        { name: 'blue'},
        { name: 'light-blue'},
        { name: 'cyan'},
        { name: 'teal'},
        { name: 'green'},
        { name: 'light-green'},
        { name: 'lime'},
        { name: 'yellow'},
        { name: 'amber'},
        { name: 'orange'},
        { name: 'deep-orange'}
    ];

    let primaryColor = localStorage.getItem('primaryColor') || 'indigo';
    let accentColor = localStorage.getItem('accentColor') || 'indigo';
    applyThemeColors(primaryColor, accentColor);

    [primaryColors, accentColors].forEach((colors, index) => {
        colors.forEach(color => {
            let selectElement = index === 0 ? primaryColorInput : accentColorInput;
            let option = document.createElement('option');
            option.value = color.name;
            option.textContent = color.name.charAt(0).toUpperCase() + color.name.slice(1);
            if ((index === 0 && color.name === primaryColor) || (index === 1 && color.name === accentColor)) {
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    });

    // 调色盘按钮点击事件
    colorPickerButton.addEventListener('click', function () {
        dialog.open();
    });

    // 应用 按钮点击事件
    applyColorButton.addEventListener('click', function () {
        primaryColor = primaryColorInput.value;
        accentColor = accentColorInput.value;
        localStorage.setItem('primaryColor', primaryColor);
        localStorage.setItem('accentColor', accentColor);
        // 应用颜色
        applyThemeColors(primaryColor, accentColor);
    });

    function applyThemeColors(primaryColor, accentColor) {
        document.body.className = '';
        document.body.classList.add(`mdui-theme-primary-${primaryColor}`);
        document.body.classList.add(`mdui-theme-accent-${accentColor}`);
    }
});
