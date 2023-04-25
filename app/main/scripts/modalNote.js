async function modalNote(response) {
    const windowInnerWidth = document.documentElement.clientWidth;
    const scrollbarWidth = parseInt(window.innerWidth) - parseInt(windowInnerWidth);

    // привязываем необходимые элементы
    const bodyElementHTML = document.getElementsByTagName("body")[0];
    const modalBackground = document.getElementsByClassName("modalBackground")[0];
    const modalClose = document.getElementsByClassName("modalClose")[0];
    const modalActiveNote = document.getElementsByClassName("modalActiveNote")[0];

    const deleteButton = document.getElementById("delete");
    const editButton = document.getElementById("edit");
    const downloadButton = document.getElementById("download");    

  // функция для корректировки положения body при появлении ползунка прокрутки
      function bodyMargin() {
          bodyElementHTML.style.marginRight = "-" + scrollbarWidth + "px";
      }

      // при длинной странице - корректируем сразу
      bodyMargin();

      // событие нажатия на триггер открытия модального окна
      // modalTrigger.addEventListener("click", 
      function openModal(){
          // делаем модальное окно видимым 
          modalBackground.style.display = "block";

          //document.cookie = `response=${response}`

          document.querySelector('.results').innerHTML = "<h3>" + response["name_notes"] + "</h3>" + "<br><br>" + "<h6>" + response["text_notes"] + "</h6>" + "<br><br>" + response["date"] + "<br><br>";

          // если размер экрана больше 1366 пикселей (т.е. на мониторе может появиться ползунок)
          if (windowInnerWidth >= 1366) {
              bodyMargin();
          }
          // позиционируем наше окно по середине, где 175 - половина ширины модального окна
          //modalActiveNote.style.left = "calc(50% - " + (375 - scrollbarWidth / 2) + "px)";
     
      }
      openModal();

      deleteButton.addEventListener("click", function() {
        window.location.assign(`/delete_note/${response.id}`);
      });

      editButton.addEventListener("click", function() {
        window.location.assign(`/update_note/${response.id}`);
      });

      downloadButton.addEventListener("click", function() {
        window.location.assign(`/download_note/${response.id}`);
      });

      
      // нажатие на крестик закрытия модального окна
      modalClose.addEventListener("click", function () {
          modalBackground.style.display = "none";
          if (windowInnerWidth >= 1366) {
            bodyMargin();
          }        
      });

      // закрытие модального окна на зону вне окна, т.е. на фон
      modalBackground.addEventListener("click", function (event) {
          if (event.target === modalBackground) {
              modalBackground.style.display = "none";
              if (windowInnerWidth >= 1366) {
                bodyMargin();
              }
          }
      });
      return;
  }