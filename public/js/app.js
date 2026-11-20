const $ = (s) => document.querySelector(s);
const messagesEl = $("#messages"), welcomeEl = $("#welcome"), input = $("#messageInput");
let activeChatId = null, busy = false;

function toast(message){const el=$("#toast");el.textContent=message;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2800)}
function scrollBottom(){const area=$("#conversation");area.scrollTop=area.scrollHeight}
function addMessage(role, content, typing=false){
  welcomeEl.style.display="none";
  const row=document.createElement("div");row.className=`message ${role}`;
  const avatar=document.createElement("div");avatar.className="message-avatar";avatar.textContent=role==="assistant"?"✦":"Y";
  const body=document.createElement("div");body.className="message-content";
  if(typing){body.classList.add("typing");body.innerHTML="<i></i><i></i><i></i>";row.dataset.typing="true";}
  else body.textContent=content;
  row.append(avatar,body);messagesEl.append(row);scrollBottom();return row;
}
function clearConversation(){messagesEl.innerHTML="";welcomeEl.style.display="block"}
async function loadChats(){
  const res=await fetch("/api/chats");const chats=await res.json();const list=$("#chatList");list.innerHTML="";
  if(!chats.length){list.innerHTML='<div class="history-empty">Your conversations will appear here.</div>';return}
  chats.forEach(chat=>{
    const item=document.createElement("div");item.className="history-item"+(chat.id===activeChatId?" active":"");
    const label=document.createElement("span");label.textContent="◷  "+chat.title;
    const del=document.createElement("button");del.className="delete-chat";del.textContent="×";del.title="Delete conversation";
    del.onclick=async(e)=>{e.stopPropagation();await fetch(`/api/chats/${chat.id}`,{method:"DELETE"});if(activeChatId===chat.id){activeChatId=null;clearConversation()}loadChats()};
    item.append(label,del);item.onclick=()=>openChat(chat.id);list.append(item);
  });
}
async function openChat(id){
  const res=await fetch(`/api/chats/${id}/messages`);if(!res.ok)return;
  const data=await res.json();activeChatId=id;clearConversation();welcomeEl.style.display="none";
  data.forEach(m=>addMessage(m.role,m.content));loadChats();
}
async function sendMessage(text){
  if(busy||!text.trim())return;busy=true;$("#sendBtn").disabled=true;
  addMessage("user",text);input.value="";input.style.height="auto";
  const typing=addMessage("assistant","",true);
  try{
    const res=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text,chat_id:activeChatId})});
    const data=await res.json();typing.remove();
    if(!res.ok){addMessage("assistant",data.error||"Something went wrong.");}
    else{activeChatId=data.chat_id;addMessage("assistant",data.reply);loadChats();}
  }catch(e){typing.remove();addMessage("assistant","I couldn't reach the server. Check your connection and try again.");}
  finally{busy=false;$("#sendBtn").disabled=false;input.focus();scrollBottom()}
}
$("#chatForm").addEventListener("submit",e=>{e.preventDefault();sendMessage(input.value)});
input.addEventListener("input",()=>{input.style.height="auto";input.style.height=Math.min(input.scrollHeight,160)+"px"});
input.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();$("#chatForm").requestSubmit()}});
$("#newChatBtn").onclick=()=>{activeChatId=null;clearConversation();loadChats();input.focus()};
document.querySelectorAll(".suggestion").forEach(btn=>btn.onclick=()=>sendMessage(btn.dataset.prompt));
$("#themeBtn").onclick=()=>document.body.classList.toggle("dark");
$("#menuBtn").onclick=()=>$("#sidebar").classList.toggle("open");
loadChats();
