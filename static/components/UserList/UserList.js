class UserListPage {
    constructor() {
        this.url = '/v1/index';
    }

    async user_creation() {
        const formData = new FormData(document.querySelector("#modal-form"));
        let myData = {};
        formData.forEach(function(value, key){
            myData[key] = value;
        });

        const response = await fetch(`/v1/manager/users/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(myData)
        });

        if (response.status !== 200) {
            errorPage.render(response);
        }
        this.modal_windows();
    }

    async getSelect() {
        const query = {
            query: `query MyQuery {
                        getEnum(nameEnumType: "UserGenderType") 
                            {
                                name 
                                value
                            }
                        }`,
            operationName: "MyQuery"
        }
        const response = await fetch(`/graphql`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(query)
        });

        if (response.status !== 200) {
            await errorPage.render(response);
        }
        const json = await response.json();
        if (json.data.error) {
            await errorPage.render(response);
            return
        }
        let select = document.createElement("select");
        select.setAttribute("class", "form-select");
        select.setAttribute("name", "gender");

        json.data.getEnum.forEach((element) => {
          let option = document.createElement("option");
          option.setAttribute("value", element.value);
          option.innerHTML = element.value
          select.append(option);
        })

        return select.outerHTML;
    }

    modal_windows() {
        let modal_launcher = document.querySelector("#modal-launcher");
        let modal_background = document.querySelector("#modal-background");
        let modal_close = document.querySelector("#modal-close");
        let modal_content = document.querySelector("#modal-content");
        modal_launcher.classList.toggle("active");
        modal_background.classList.toggle("active");
        modal_close.classList.toggle("active");
        modal_content.classList.toggle("active");
    }

    user_update() {
        userListPage.fill_data();
    }

    async fill_data() {
        // Описание таблицы
        let table_template = [
            { "head": "Логин", "row": "name" },
            { "head": "Электронная почта", "row": "email" },
            { "head": "Пол", "row": "gender" },
            { "head": "Дата создания", "row": "created_at" },
            { "head": "Возраст", "row": "age" },
            { "head": "Описание", "row": "description" },
            { "head": "Полные права", "row": "is_admin" },
            { "head": "Аккаунт активирован", "row": "is_active" }]
        // Структура шаблона
        // <thead>
        //      <tr>
        //         <th></th>
        //      </th>
        // </thead>
        // <tbody>
        //      <tr>
        //         <td "data-value"=""></td>
        //      </tr>
        // </tbody>

        const response = await fetch(`/v1/users/list`, {
            method: 'GET'
        });

        if (response.status !== 200) {
            errorPage.render(response)
        } else {
            let user_list = await response.json();
            let table_users = document.querySelector("#table_users");
            table_users.innerHTML = '';

            let table_thead = document.createElement("thead");
            let tr_head = document.createElement("tr");
            table_thead.append(tr_head);
            table_users.append(table_thead);

            let table_tbody = document.createElement("tbody");
            let tr_body = document.createElement("tr");
            table_tbody.append(tr_body);
            table_users.append(table_tbody);

            for (let row_tmpl of table_template) {
                let th = document.createElement("th");
                th.innerHTML = row_tmpl.head;
                tr_head.append(th);

                let td = document.createElement("td");
                td.setAttribute("data-value", row_tmpl.row);
                tr_body.append(td);
            }

            let table_row = table_tbody.querySelector("tr");
            for (let row of user_list) {
                let tmpl_row = table_row.cloneNode(true);
                for (let td of tmpl_row.querySelectorAll("td")) {
                    td.innerHTML = row[td.dataset.value];
                }

                table_tbody.append(tmpl_row);
            }
            // Удаляем шаблон
            table_row.remove();
        }
    }

    async render() {
        let buttonUserCreation = String.raw`
        <button onclick="userListPage.modal_windows();" class="btn btn-info"  id="modal-launcher">          
            <span> Создать нового пользователя </span>
       </button>
       `;

        let buttonUserUpdate = String.raw`
        <button onclick="userListPage.user_update();" class="btn btn-info">          
            <span> Обновить </span>
        </button>
        `;

        // console.log(userListPage.getSelect());

        let selectGender = await userListPage.getSelect();

        ROOT_USER_LIST.innerHTML = String.raw`   
            ${buttonUserCreation}
            ${buttonUserUpdate}
            <hr>
            <div>
                <h3>Список пользователей</h3>
                <table id="table_users" class="table table-bordered"> 
                     <!-- Здесь будут сгенерированы элементы -->       
                </table>       
            </div> 
            <div id="modal-background"></div>
            <div id="modal-content">
            <form id="modal-form" method="GET" action="">
                <div class="row mb-3">
                    <label for="inputName" class="col-sm-2 col-form-label">Имя</label>
                    <div class="col-sm-10">
                        <input type="text" class="form-control" name="name">
                        ${selectGender}
                        <input type="email" class="form-control" name="email">
                        <input type="password" class="form-control" name="password">
                        <input type="datetime-local" class="form-control" name="created_at">
                        <input type="number" class="form-control" name="age" value="25">
                        <input type="text" class="form-control" name="description" value="Yes">
                        <input type="checkbox" checked value="true" name="is_admin">
                        <input type="hidden" value="false" name="is_admin">
                        <input type="checkbox" name="is_active" value="true" checked>  
                        <input type="hidden" name="is_active" value="false" >     
                    </div>
                </div>
                <br>
                <button type="submit" class="btn btn-primary" onclick="userListPage.user_creation();">Создать</button>
                <button id="modal-close" onclick="userListPage.modal_windows();">Отмена</button>
            </form>
            </div>
        `;
              
        userListPage.fill_data();
    }
}

const userListPage = new UserListPage();