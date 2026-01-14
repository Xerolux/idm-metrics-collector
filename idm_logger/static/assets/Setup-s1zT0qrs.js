import{B as _,k as D,l as T,g as x,o as u,w as h,a as g,h as k,m,f as o,p as y,q as U,n as E,s as C,T as M,v as N,r as P,b as i,d,e as F,j as V,F as S,x as I,t as $,y as L}from"./index-mB4EineT.js";import{s as W}from"./index-ChmEyEl_.js";import{s as f}from"./index-CVKqlFlT.js";import{s as R}from"./index-A0BGJiN0.js";import{R as Z,a as G,f as H,s as K}from"./index-CNTwlNF5.js";import{s as q}from"./index-13QzdPYA.js";import{s as J}from"./index-DzOcsC1r.js";import{s as z}from"./index-kMUmKRVM.js";import{A as Q}from"./AppFooter-DJh2_xi1.js";import"./index-Dl2_alcG.js";import"./index-CLs7nh7g.js";var X=`
    .p-message {
        display: grid;
        grid-template-rows: 1fr;
        border-radius: dt('message.border.radius');
        outline-width: dt('message.border.width');
        outline-style: solid;
    }

    .p-message-content-wrapper {
        min-height: 0;
    }

    .p-message-content {
        display: flex;
        align-items: center;
        padding: dt('message.content.padding');
        gap: dt('message.content.gap');
    }

    .p-message-icon {
        flex-shrink: 0;
    }

    .p-message-close-button {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-inline-start: auto;
        overflow: hidden;
        position: relative;
        width: dt('message.close.button.width');
        height: dt('message.close.button.height');
        border-radius: dt('message.close.button.border.radius');
        background: transparent;
        transition:
            background dt('message.transition.duration'),
            color dt('message.transition.duration'),
            outline-color dt('message.transition.duration'),
            box-shadow dt('message.transition.duration'),
            opacity 0.3s;
        outline-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-message-close-icon {
        font-size: dt('message.close.icon.size');
        width: dt('message.close.icon.size');
        height: dt('message.close.icon.size');
    }

    .p-message-close-button:focus-visible {
        outline-width: dt('message.close.button.focus.ring.width');
        outline-style: dt('message.close.button.focus.ring.style');
        outline-offset: dt('message.close.button.focus.ring.offset');
    }

    .p-message-info {
        background: dt('message.info.background');
        outline-color: dt('message.info.border.color');
        color: dt('message.info.color');
        box-shadow: dt('message.info.shadow');
    }

    .p-message-info .p-message-close-button:focus-visible {
        outline-color: dt('message.info.close.button.focus.ring.color');
        box-shadow: dt('message.info.close.button.focus.ring.shadow');
    }

    .p-message-info .p-message-close-button:hover {
        background: dt('message.info.close.button.hover.background');
    }

    .p-message-info.p-message-outlined {
        color: dt('message.info.outlined.color');
        outline-color: dt('message.info.outlined.border.color');
    }

    .p-message-info.p-message-simple {
        color: dt('message.info.simple.color');
    }

    .p-message-success {
        background: dt('message.success.background');
        outline-color: dt('message.success.border.color');
        color: dt('message.success.color');
        box-shadow: dt('message.success.shadow');
    }

    .p-message-success .p-message-close-button:focus-visible {
        outline-color: dt('message.success.close.button.focus.ring.color');
        box-shadow: dt('message.success.close.button.focus.ring.shadow');
    }

    .p-message-success .p-message-close-button:hover {
        background: dt('message.success.close.button.hover.background');
    }

    .p-message-success.p-message-outlined {
        color: dt('message.success.outlined.color');
        outline-color: dt('message.success.outlined.border.color');
    }

    .p-message-success.p-message-simple {
        color: dt('message.success.simple.color');
    }

    .p-message-warn {
        background: dt('message.warn.background');
        outline-color: dt('message.warn.border.color');
        color: dt('message.warn.color');
        box-shadow: dt('message.warn.shadow');
    }

    .p-message-warn .p-message-close-button:focus-visible {
        outline-color: dt('message.warn.close.button.focus.ring.color');
        box-shadow: dt('message.warn.close.button.focus.ring.shadow');
    }

    .p-message-warn .p-message-close-button:hover {
        background: dt('message.warn.close.button.hover.background');
    }

    .p-message-warn.p-message-outlined {
        color: dt('message.warn.outlined.color');
        outline-color: dt('message.warn.outlined.border.color');
    }

    .p-message-warn.p-message-simple {
        color: dt('message.warn.simple.color');
    }

    .p-message-error {
        background: dt('message.error.background');
        outline-color: dt('message.error.border.color');
        color: dt('message.error.color');
        box-shadow: dt('message.error.shadow');
    }

    .p-message-error .p-message-close-button:focus-visible {
        outline-color: dt('message.error.close.button.focus.ring.color');
        box-shadow: dt('message.error.close.button.focus.ring.shadow');
    }

    .p-message-error .p-message-close-button:hover {
        background: dt('message.error.close.button.hover.background');
    }

    .p-message-error.p-message-outlined {
        color: dt('message.error.outlined.color');
        outline-color: dt('message.error.outlined.border.color');
    }

    .p-message-error.p-message-simple {
        color: dt('message.error.simple.color');
    }

    .p-message-secondary {
        background: dt('message.secondary.background');
        outline-color: dt('message.secondary.border.color');
        color: dt('message.secondary.color');
        box-shadow: dt('message.secondary.shadow');
    }

    .p-message-secondary .p-message-close-button:focus-visible {
        outline-color: dt('message.secondary.close.button.focus.ring.color');
        box-shadow: dt('message.secondary.close.button.focus.ring.shadow');
    }

    .p-message-secondary .p-message-close-button:hover {
        background: dt('message.secondary.close.button.hover.background');
    }

    .p-message-secondary.p-message-outlined {
        color: dt('message.secondary.outlined.color');
        outline-color: dt('message.secondary.outlined.border.color');
    }

    .p-message-secondary.p-message-simple {
        color: dt('message.secondary.simple.color');
    }

    .p-message-contrast {
        background: dt('message.contrast.background');
        outline-color: dt('message.contrast.border.color');
        color: dt('message.contrast.color');
        box-shadow: dt('message.contrast.shadow');
    }

    .p-message-contrast .p-message-close-button:focus-visible {
        outline-color: dt('message.contrast.close.button.focus.ring.color');
        box-shadow: dt('message.contrast.close.button.focus.ring.shadow');
    }

    .p-message-contrast .p-message-close-button:hover {
        background: dt('message.contrast.close.button.hover.background');
    }

    .p-message-contrast.p-message-outlined {
        color: dt('message.contrast.outlined.color');
        outline-color: dt('message.contrast.outlined.border.color');
    }

    .p-message-contrast.p-message-simple {
        color: dt('message.contrast.simple.color');
    }

    .p-message-text {
        font-size: dt('message.text.font.size');
        font-weight: dt('message.text.font.weight');
    }

    .p-message-icon {
        font-size: dt('message.icon.size');
        width: dt('message.icon.size');
        height: dt('message.icon.size');
    }

    .p-message-sm .p-message-content {
        padding: dt('message.content.sm.padding');
    }

    .p-message-sm .p-message-text {
        font-size: dt('message.text.sm.font.size');
    }

    .p-message-sm .p-message-icon {
        font-size: dt('message.icon.sm.size');
        width: dt('message.icon.sm.size');
        height: dt('message.icon.sm.size');
    }

    .p-message-sm .p-message-close-icon {
        font-size: dt('message.close.icon.sm.size');
        width: dt('message.close.icon.sm.size');
        height: dt('message.close.icon.sm.size');
    }

    .p-message-lg .p-message-content {
        padding: dt('message.content.lg.padding');
    }

    .p-message-lg .p-message-text {
        font-size: dt('message.text.lg.font.size');
    }

    .p-message-lg .p-message-icon {
        font-size: dt('message.icon.lg.size');
        width: dt('message.icon.lg.size');
        height: dt('message.icon.lg.size');
    }

    .p-message-lg .p-message-close-icon {
        font-size: dt('message.close.icon.lg.size');
        width: dt('message.close.icon.lg.size');
        height: dt('message.close.icon.lg.size');
    }

    .p-message-outlined {
        background: transparent;
        outline-width: dt('message.outlined.border.width');
    }

    .p-message-simple {
        background: transparent;
        outline-color: transparent;
        box-shadow: none;
    }

    .p-message-simple .p-message-content {
        padding: dt('message.simple.content.padding');
    }

    .p-message-outlined .p-message-close-button:hover,
    .p-message-simple .p-message-close-button:hover {
        background: transparent;
    }

    .p-message-enter-active {
        animation: p-animate-message-enter 0.3s ease-out forwards;
        overflow: hidden;
    }

    .p-message-leave-active {
        animation: p-animate-message-leave 0.15s ease-in forwards;
        overflow: hidden;
    }

    @keyframes p-animate-message-enter {
        from {
            opacity: 0;
            grid-template-rows: 0fr;
        }
        to {
            opacity: 1;
            grid-template-rows: 1fr;
        }
    }

    @keyframes p-animate-message-leave {
        from {
            opacity: 1;
            grid-template-rows: 1fr;
        }
        to {
            opacity: 0;
            margin: 0;
            grid-template-rows: 0fr;
        }
    }
`,Y={root:function(s){var t=s.props;return["p-message p-component p-message-"+t.severity,{"p-message-outlined":t.variant==="outlined","p-message-simple":t.variant==="simple","p-message-sm":t.size==="small","p-message-lg":t.size==="large"}]},contentWrapper:"p-message-content-wrapper",content:"p-message-content",icon:"p-message-icon",text:"p-message-text",closeButton:"p-message-close-button",closeIcon:"p-message-close-icon"},ee=_.extend({name:"message",style:X,classes:Y}),se={name:"BaseMessage",extends:G,props:{severity:{type:String,default:"info"},closable:{type:Boolean,default:!1},life:{type:Number,default:null},icon:{type:String,default:void 0},closeIcon:{type:String,default:void 0},closeButtonProps:{type:null,default:null},size:{type:String,default:null},variant:{type:String,default:null}},style:ee,provide:function(){return{$pcMessage:this,$parentInstance:this}}};function b(e){"@babel/helpers - typeof";return b=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(s){return typeof s}:function(s){return s&&typeof Symbol=="function"&&s.constructor===Symbol&&s!==Symbol.prototype?"symbol":typeof s},b(e)}function j(e,s,t){return(s=ne(s))in e?Object.defineProperty(e,s,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[s]=t,e}function ne(e){var s=oe(e,"string");return b(s)=="symbol"?s:s+""}function oe(e,s){if(b(e)!="object"||!e)return e;var t=e[Symbol.toPrimitive];if(t!==void 0){var l=t.call(e,s);if(b(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(s==="string"?String:Number)(e)}var A={name:"Message",extends:se,inheritAttrs:!1,emits:["close","life-end"],timeout:null,data:function(){return{visible:!0}},mounted:function(){var s=this;this.life&&setTimeout(function(){s.visible=!1,s.$emit("life-end")},this.life)},methods:{close:function(s){this.visible=!1,this.$emit("close",s)}},computed:{closeAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.close:void 0},dataP:function(){return H(j(j({outlined:this.variant==="outlined",simple:this.variant==="simple"},this.severity,this.severity),this.size,this.size))}},directives:{ripple:Z},components:{TimesIcon:q}};function v(e){"@babel/helpers - typeof";return v=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(s){return typeof s}:function(s){return s&&typeof Symbol=="function"&&s.constructor===Symbol&&s!==Symbol.prototype?"symbol":typeof s},v(e)}function O(e,s){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);s&&(l=l.filter(function(r){return Object.getOwnPropertyDescriptor(e,r).enumerable})),t.push.apply(t,l)}return t}function B(e){for(var s=1;s<arguments.length;s++){var t=arguments[s]!=null?arguments[s]:{};s%2?O(Object(t),!0).forEach(function(l){te(e,l,t[l])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):O(Object(t)).forEach(function(l){Object.defineProperty(e,l,Object.getOwnPropertyDescriptor(t,l))})}return e}function te(e,s,t){return(s=ae(s))in e?Object.defineProperty(e,s,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[s]=t,e}function ae(e){var s=re(e,"string");return v(s)=="symbol"?s:s+""}function re(e,s){if(v(e)!="object"||!e)return e;var t=e[Symbol.toPrimitive];if(t!==void 0){var l=t.call(e,s);if(v(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(s==="string"?String:Number)(e)}var le=["data-p"],ie=["data-p"],de=["data-p"],ce=["aria-label","data-p"],ue=["data-p"];function me(e,s,t,l,r,c){var p=D("TimesIcon"),n=T("ripple");return u(),x(M,m({name:"p-message",appear:""},e.ptmi("transition")),{default:h(function(){return[r.visible?(u(),g("div",m({key:0,class:e.cx("root"),role:"alert","aria-live":"assertive","aria-atomic":"true","data-p":c.dataP},e.ptm("root")),[o("div",m({class:e.cx("contentWrapper")},e.ptm("contentWrapper")),[e.$slots.container?y(e.$slots,"container",{key:0,closeCallback:c.close}):(u(),g("div",m({key:1,class:e.cx("content"),"data-p":c.dataP},e.ptm("content")),[y(e.$slots,"icon",{class:E(e.cx("icon"))},function(){return[(u(),x(C(e.icon?"span":null),m({class:[e.cx("icon"),e.icon],"data-p":c.dataP},e.ptm("icon")),null,16,["class","data-p"]))]}),e.$slots.default?(u(),g("div",m({key:0,class:e.cx("text"),"data-p":c.dataP},e.ptm("text")),[y(e.$slots,"default")],16,de)):k("",!0),e.closable?U((u(),g("button",m({key:1,class:e.cx("closeButton"),"aria-label":c.closeAriaLabel,type:"button",onClick:s[0]||(s[0]=function(a){return c.close(a)}),"data-p":c.dataP},B(B({},e.closeButtonProps),e.ptm("closeButton"))),[y(e.$slots,"closeicon",{},function(){return[e.closeIcon?(u(),g("i",m({key:0,class:[e.cx("closeIcon"),e.closeIcon],"data-p":c.dataP},e.ptm("closeIcon")),null,16,ue)):(u(),x(p,m({key:1,class:[e.cx("closeIcon"),e.closeIcon],"data-p":c.dataP},e.ptm("closeIcon")),null,16,["class","data-p"]))]})],16,ce)),[[n]]):k("",!0)],16,ie))],16)],16,le)):k("",!0)]}),_:3},16)}A.render=me;const ge={class:"flex flex-col items-center justify-center min-h-screen bg-gray-900 p-4"},pe={class:"flex flex-col gap-6"},fe={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},be={class:"flex flex-col gap-2"},ve={class:"flex flex-col gap-2"},ye={class:"flex flex-col gap-2"},he={class:"flex flex-col gap-2"},we={class:"flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50"},xe={class:"flex items-center gap-2"},ke={class:"flex flex-wrap gap-4"},ze=["for"],Pe={class:"flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50"},Ve={class:"flex flex-wrap gap-4"},Se=["for"],Ie={class:"flex flex-col gap-2"},$e={class:"flex flex-col gap-2"},je={class:"flex flex-col gap-2"},Oe={class:"flex flex-col gap-2"},Be={class:"flex flex-col gap-2"},Ae={class:"flex flex-col gap-2 border-t border-gray-700 pt-4"},_e={class:"flex flex-col gap-2"},De={class:"flex justify-end pt-4"},Ge={__name:"Setup",setup(e){const s=F(),t=N(),l=P(!1),r=P({idm_host:"",idm_port:502,circuits:["A"],zones:[],influx_url:"http://localhost:8086",influx_org:"home",influx_bucket:"idm",influx_token:"",password:""}),c=async()=>{if(r.value.password.length<6){t.add({severity:"warn",summary:"Ungültig",detail:"Passwort muss mindestens 6 Zeichen lang sein",life:3e3});return}l.value=!0;try{(await L.post("/api/setup",r.value)).data.success&&(t.add({severity:"success",summary:"Erfolg",detail:"Einrichtung abgeschlossen",life:3e3}),setTimeout(()=>{s.push("/login")},1e3))}catch(p){t.add({severity:"error",summary:"Fehler",detail:p.response?.data?.error||p.message,life:5e3})}finally{l.value=!1}};return(p,n)=>(u(),g("div",ge,[i(d(W),{class:"w-full max-w-2xl bg-gray-800 border-gray-700 text-white mb-auto mt-auto"},{title:h(()=>[...n[10]||(n[10]=[V("Ersteinrichtung",-1)])]),content:h(()=>[o("div",pe,[i(d(A),{severity:"info",closable:!1},{default:h(()=>[...n[11]||(n[11]=[V("Willkommen beim IDM Logger. Bitte konfiguriere die Grundeinstellungen.",-1)])]),_:1}),o("div",fe,[o("div",be,[n[17]||(n[17]=o("label",{class:"font-bold text-blue-400"},"IDM Wärmepumpe",-1)),o("div",ve,[n[12]||(n[12]=o("label",null,"Host IP",-1)),i(d(f),{modelValue:r.value.idm_host,"onUpdate:modelValue":n[0]||(n[0]=a=>r.value.idm_host=a),placeholder:"192.168.x.x"},null,8,["modelValue"])]),o("div",ye,[n[13]||(n[13]=o("label",null,"Modbus Port",-1)),i(d(R),{modelValue:r.value.idm_port,"onUpdate:modelValue":n[1]||(n[1]=a=>r.value.idm_port=a),useGrouping:!1},null,8,["modelValue"])]),o("div",he,[n[16]||(n[16]=o("label",{class:"font-bold"},"Aktivierte Features",-1)),o("div",we,[o("div",xe,[i(d(z),{modelValue:r.value.circuits,"onUpdate:modelValue":n[2]||(n[2]=a=>r.value.circuits=a),inputId:"circuitA",value:"A",disabled:""},null,8,["modelValue"]),n[14]||(n[14]=o("label",{for:"circuitA",class:"opacity-50"},"Heizkreis A (Immer aktiv)",-1))]),o("div",ke,[(u(),g(S,null,I(["B","C","D","E","F","G"],a=>o("div",{key:a,class:"flex items-center gap-2"},[i(d(z),{modelValue:r.value.circuits,"onUpdate:modelValue":n[3]||(n[3]=w=>r.value.circuits=w),inputId:"circuit"+a,value:a},null,8,["modelValue","inputId","value"]),o("label",{for:"circuit"+a},"Heizkreis "+$(a),9,ze)])),64))])]),o("div",Pe,[n[15]||(n[15]=o("label",{class:"text-sm text-gray-400"},"Zonenmodule",-1)),o("div",Ve,[(u(),g(S,null,I(10,a=>o("div",{key:a,class:"flex items-center gap-2"},[i(d(z),{modelValue:r.value.zones,"onUpdate:modelValue":n[4]||(n[4]=w=>r.value.zones=w),inputId:"zone"+(a-1),value:a-1},null,8,["modelValue","inputId","value"]),o("label",{for:"zone"+(a-1)},"Zone "+$(a),9,Se)])),64))])])])]),o("div",Ie,[n[22]||(n[22]=o("label",{class:"font-bold text-green-400"},"InfluxDB v2",-1)),o("div",$e,[n[18]||(n[18]=o("label",null,"URL",-1)),i(d(f),{modelValue:r.value.influx_url,"onUpdate:modelValue":n[5]||(n[5]=a=>r.value.influx_url=a),placeholder:"http://localhost:8086"},null,8,["modelValue"])]),o("div",je,[n[19]||(n[19]=o("label",null,"Organisation",-1)),i(d(f),{modelValue:r.value.influx_org,"onUpdate:modelValue":n[6]||(n[6]=a=>r.value.influx_org=a)},null,8,["modelValue"])]),o("div",Oe,[n[20]||(n[20]=o("label",null,"Bucket",-1)),i(d(f),{modelValue:r.value.influx_bucket,"onUpdate:modelValue":n[7]||(n[7]=a=>r.value.influx_bucket=a)},null,8,["modelValue"])]),o("div",Be,[n[21]||(n[21]=o("label",null,"Token",-1)),i(d(f),{modelValue:r.value.influx_token,"onUpdate:modelValue":n[8]||(n[8]=a=>r.value.influx_token=a),type:"password"},null,8,["modelValue"])])])]),o("div",Ae,[n[25]||(n[25]=o("label",{class:"font-bold text-red-400"},"Admin Sicherheit",-1)),o("div",_e,[n[23]||(n[23]=o("label",null,"Admin Passwort",-1)),i(d(f),{modelValue:r.value.password,"onUpdate:modelValue":n[9]||(n[9]=a=>r.value.password=a),type:"password",placeholder:"Wähle ein sicheres Passwort"},null,8,["modelValue"]),n[24]||(n[24]=o("small",{class:"text-gray-400"},"Mindestens 6 Zeichen.",-1))])]),o("div",De,[i(d(K),{label:"Einrichtung abschließen",icon:"pi pi-check",onClick:c,loading:l.value},null,8,["loading"])])])]),_:1}),i(d(J)),i(Q)]))}};export{Ge as default};
