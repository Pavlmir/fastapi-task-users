function render() {
    headerPage.render();  
    if (window.location.pathname === '/') {
        loginPage.render();
    } else if (window.location.pathname === userListPage.url) {
        userListPage.render();
    }
}

render();
