var last_form = null;
document.addEventListener('DOMContentLoaded', function () {
    
    //Select like divs and give onclick command
    document.querySelectorAll('.fa-heart').forEach(div => {
        div.onclick = function () {
            likeDislike(this);
            //console.log('like')
        };
    });
    //like function activated once the div is clicked
    const likeDislike = (element) => {
        fetch(`/like/${element.dataset.id}/`)
        .then(response => response.json())
        .then(data => {
            element.className = data.css_marker;
            element.querySelector('small').innerHTML = data.total_likes;
        });
    }

    
    //selecting the follow button and adjusting the inner html for followers upon click
    document.querySelectorAll('#btnfollow').forEach(button => {
        button.onclick = function () {
            //console.log('follow')
            fetch(`/follow/${this.dataset.id}`)
                .then(response => response.json())
                .then(data => {
                    document.querySelector('#sp_followers').innerHTML = data.total_followers;
                    console.log(data.result)
                    if (data.result == "follow") {
                        this.innerHTML = "Unfollow";
                    } 
                    else {
                        this.innerHTML = "Follow";
                    }
                });
        };
    })


    //Using query selector to add onclick event listener to all posts from user
    document.querySelectorAll('.edit_post').forEach(div => {
        div.onclick = function () {
            //console.log('inside of edit post div')
            edit(id(this));
        };
    });
    //This runction returns the id of any given post for editing purpuses
    const id = (element) => {
        console.log('inside of id function')
        //console.log(element.id)
        return element.id
        }
    
    //Using the edit function to updaate user posts, and put to update the specified post in the database
    function edit(id) {
        console.log('inside edit function')
        console.log(id)
        var edit_box = document.querySelector(`#edit-box-${id}`);
        var edit_btn = document.querySelector(`#edit-btn-${id}`);
        edit_box.style.display = 'block';
        edit_btn.style.display = 'block';

        edit_btn.addEventListener('click', () => {
            //console.log('inside btn click event listener')
            fetch('/edit/' + id, {
                method: 'PUT',
                body: JSON.stringify({
                    post: edit_box.value

                })
            });
            
            edit_box.style.display = 'none';
            edit_btn.style.display = 'none';

            document.querySelector(`#post-text-${id}`).innerHTML = edit_box.value;
        });

        edit_box.value = "";
    }
});