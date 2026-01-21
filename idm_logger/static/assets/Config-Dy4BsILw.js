import{a as f,o as b,f as n,m as v,B as H,l as ke,b as d,p as L,h as k,q as z,t as P,n as j,g as O,s as K,w as y,ag as Ve,T as st,aa as Z,ah as Ue,D as dt,A as ze,ai as le,F as U,x as F,X as ae,z as Oe,a5 as ne,k as ut,a6 as pt,r as h,v as ct,U as bt,c as ft,L as gt,K as vt,y as _,d as s,j as $}from"./index-Dq30hFFt.js";import{a as mt,s as V}from"./index-DZCqU46w.js";import{b as _e,R as re,a as Te,f as ie,s as T}from"./index-JacqIPAm.js";import{a as yt,b as Fe,s as w}from"./index-CSmoGcvh.js";import{s as q}from"./index-DYXQjfhZ.js";import{s as ht}from"./index-BrFMq7zu.js";import{s as xt}from"./index-Bq9Qd724.js";import{s as Ee}from"./index-CytOEFXu.js";import"./index-JzF1hPun.js";import"./index-BJdHXrtG.js";var He={name:"PlusIcon",extends:_e};function wt(t){return Tt(t)||_t(t)||Vt(t)||kt()}function kt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Vt(t,e){if(t){if(typeof t=="string")return me(t,e);var a={}.toString.call(t).slice(8,-1);return a==="Object"&&t.constructor&&(a=t.constructor.name),a==="Map"||a==="Set"?Array.from(t):a==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(a)?me(t,e):void 0}}function _t(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Tt(t){if(Array.isArray(t))return me(t)}function me(t,e){(e==null||e>t.length)&&(e=t.length);for(var a=0,o=Array(e);a<e;a++)o[a]=t[a];return o}function Pt(t,e,a,o,p,i){return b(),f("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),wt(e[0]||(e[0]=[n("path",{d:"M7.67742 6.32258V0.677419C7.67742 0.497757 7.60605 0.325452 7.47901 0.198411C7.35197 0.0713707 7.17966 0 7 0C6.82034 0 6.64803 0.0713707 6.52099 0.198411C6.39395 0.325452 6.32258 0.497757 6.32258 0.677419V6.32258H0.677419C0.497757 6.32258 0.325452 6.39395 0.198411 6.52099C0.0713707 6.64803 0 6.82034 0 7C0 7.17966 0.0713707 7.35197 0.198411 7.47901C0.325452 7.60605 0.497757 7.67742 0.677419 7.67742H6.32258V13.3226C6.32492 13.5015 6.39704 13.6725 6.52358 13.799C6.65012 13.9255 6.82106 13.9977 7 14C7.17966 14 7.35197 13.9286 7.47901 13.8016C7.60605 13.6745 7.67742 13.5022 7.67742 13.3226V7.67742H13.3226C13.5022 7.67742 13.6745 7.60605 13.8016 7.47901C13.9286 7.35197 14 7.17966 14 7C13.9977 6.82106 13.9255 6.65012 13.799 6.52358C13.6725 6.39704 13.5015 6.32492 13.3226 6.32258H7.67742Z",fill:"currentColor"},null,-1)])),16)}He.render=Pt;var St=`
    .p-fieldset {
        background: dt('fieldset.background');
        border: 1px solid dt('fieldset.border.color');
        border-radius: dt('fieldset.border.radius');
        color: dt('fieldset.color');
        padding: dt('fieldset.padding');
        margin: 0;
    }

    .p-fieldset-legend {
        background: dt('fieldset.legend.background');
        border-radius: dt('fieldset.legend.border.radius');
        border-width: dt('fieldset.legend.border.width');
        border-style: solid;
        border-color: dt('fieldset.legend.border.color');
        padding: dt('fieldset.legend.padding');
        transition:
            background dt('fieldset.transition.duration'),
            color dt('fieldset.transition.duration'),
            outline-color dt('fieldset.transition.duration'),
            box-shadow dt('fieldset.transition.duration');
    }

    .p-fieldset-toggleable > .p-fieldset-legend {
        padding: 0;
    }

    .p-fieldset-toggle-button {
        cursor: pointer;
        user-select: none;
        overflow: hidden;
        position: relative;
        text-decoration: none;
        display: flex;
        gap: dt('fieldset.legend.gap');
        align-items: center;
        justify-content: center;
        padding: dt('fieldset.legend.padding');
        background: transparent;
        border: 0 none;
        border-radius: dt('fieldset.legend.border.radius');
        transition:
            background dt('fieldset.transition.duration'),
            color dt('fieldset.transition.duration'),
            outline-color dt('fieldset.transition.duration'),
            box-shadow dt('fieldset.transition.duration');
        outline-color: transparent;
    }

    .p-fieldset-legend-label {
        font-weight: dt('fieldset.legend.font.weight');
    }

    .p-fieldset-toggle-button:focus-visible {
        box-shadow: dt('fieldset.legend.focus.ring.shadow');
        outline: dt('fieldset.legend.focus.ring.width') dt('fieldset.legend.focus.ring.style') dt('fieldset.legend.focus.ring.color');
        outline-offset: dt('fieldset.legend.focus.ring.offset');
    }

    .p-fieldset-toggleable > .p-fieldset-legend:hover {
        color: dt('fieldset.legend.hover.color');
        background: dt('fieldset.legend.hover.background');
    }

    .p-fieldset-toggle-icon {
        color: dt('fieldset.toggle.icon.color');
        transition: color dt('fieldset.transition.duration');
    }

    .p-fieldset-toggleable > .p-fieldset-legend:hover .p-fieldset-toggle-icon {
        color: dt('fieldset.toggle.icon.hover.color');
    }

    .p-fieldset-content-container {
        display: grid;
        grid-template-rows: 1fr;
    }

    .p-fieldset-content-wrapper {
        min-height: 0;
    }

    .p-fieldset-content {
        padding: dt('fieldset.content.padding');
    }
`,$t={root:function(e){var a=e.props;return["p-fieldset p-component",{"p-fieldset-toggleable":a.toggleable}]},legend:"p-fieldset-legend",legendLabel:"p-fieldset-legend-label",toggleButton:"p-fieldset-toggle-button",toggleIcon:"p-fieldset-toggle-icon",contentContainer:"p-fieldset-content-container",contentWrapper:"p-fieldset-content-wrapper",content:"p-fieldset-content"},At=H.extend({name:"fieldset",style:St,classes:$t}),Ct={name:"BaseFieldset",extends:Te,props:{legend:String,toggleable:Boolean,collapsed:Boolean,toggleButtonProps:{type:null,default:null}},style:At,provide:function(){return{$pcFieldset:this,$parentInstance:this}}},I={name:"Fieldset",extends:Ct,inheritAttrs:!1,emits:["update:collapsed","toggle"],data:function(){return{d_collapsed:this.collapsed}},watch:{collapsed:function(e){this.d_collapsed=e}},methods:{toggle:function(e){this.d_collapsed=!this.d_collapsed,this.$emit("update:collapsed",this.d_collapsed),this.$emit("toggle",{originalEvent:e,value:this.d_collapsed})},onKeyDown:function(e){(e.code==="Enter"||e.code==="NumpadEnter"||e.code==="Space")&&(this.toggle(e),e.preventDefault())}},computed:{buttonAriaLabel:function(){return this.toggleButtonProps&&this.toggleButtonProps.ariaLabel?this.toggleButtonProps.ariaLabel:this.legend},dataP:function(){return ie({toggleable:this.toggleable})}},directives:{ripple:re},components:{PlusIcon:He,MinusIcon:mt}};function G(t){"@babel/helpers - typeof";return G=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},G(t)}function je(t,e){var a=Object.keys(t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);e&&(o=o.filter(function(p){return Object.getOwnPropertyDescriptor(t,p).enumerable})),a.push.apply(a,o)}return a}function qe(t){for(var e=1;e<arguments.length;e++){var a=arguments[e]!=null?arguments[e]:{};e%2?je(Object(a),!0).forEach(function(o){It(t,o,a[o])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(a)):je(Object(a)).forEach(function(o){Object.defineProperty(t,o,Object.getOwnPropertyDescriptor(a,o))})}return t}function It(t,e,a){return(e=Bt(e))in t?Object.defineProperty(t,e,{value:a,enumerable:!0,configurable:!0,writable:!0}):t[e]=a,t}function Bt(t){var e=Lt(t,"string");return G(e)=="symbol"?e:e+""}function Lt(t,e){if(G(t)!="object"||!t)return t;var a=t[Symbol.toPrimitive];if(a!==void 0){var o=a.call(t,e);if(G(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var Dt=["data-p"],Ut=["data-p"],zt=["id"],Ot=["id","aria-controls","aria-expanded","aria-label"],Et=["id","aria-labelledby"];function jt(t,e,a,o,p,i){var x=ke("ripple");return b(),f("fieldset",v({class:t.cx("root"),"data-p":i.dataP},t.ptmi("root")),[n("legend",v({class:t.cx("legend"),"data-p":i.dataP},t.ptm("legend")),[L(t.$slots,"legend",{toggleCallback:i.toggle},function(){return[t.toggleable?k("",!0):(b(),f("span",v({key:0,id:t.$id+"_header",class:t.cx("legendLabel")},t.ptm("legendLabel")),P(t.legend),17,zt)),t.toggleable?z((b(),f("button",v({key:1,id:t.$id+"_header",type:"button","aria-controls":t.$id+"_content","aria-expanded":!p.d_collapsed,"aria-label":i.buttonAriaLabel,class:t.cx("toggleButton"),onClick:e[0]||(e[0]=function(){return i.toggle&&i.toggle.apply(i,arguments)}),onKeydown:e[1]||(e[1]=function(){return i.onKeyDown&&i.onKeyDown.apply(i,arguments)})},qe(qe({},t.toggleButtonProps),t.ptm("toggleButton"))),[L(t.$slots,t.$slots.toggleicon?"toggleicon":"togglericon",{collapsed:p.d_collapsed,class:j(t.cx("toggleIcon"))},function(){return[(b(),O(K(p.d_collapsed?"PlusIcon":"MinusIcon"),v({class:t.cx("toggleIcon")},t.ptm("toggleIcon")),null,16,["class"]))]}),n("span",v({class:t.cx("legendLabel")},t.ptm("legendLabel")),P(t.legend),17)],16,Ot)),[[x]]):k("",!0)]})],16,Ut),d(st,v({name:"p-collapsible"},t.ptm("transition")),{default:y(function(){return[z(n("div",v({id:t.$id+"_content",class:t.cx("contentContainer"),role:"region","aria-labelledby":t.$id+"_header"},t.ptm("contentContainer")),[n("div",v({class:t.cx("contentWrapper")},t.ptm("contentWrapper")),[n("div",v({class:t.cx("content")},t.ptm("content")),[L(t.$slots,"default")],16)],16)],16,Et),[[Ve,!p.d_collapsed]])]}),_:3},16)],16,Dt)}I.render=jt;var qt=`
    .p-textarea {
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: dt('textarea.color');
        background: dt('textarea.background');
        padding-block: dt('textarea.padding.y');
        padding-inline: dt('textarea.padding.x');
        border: 1px solid dt('textarea.border.color');
        transition:
            background dt('textarea.transition.duration'),
            color dt('textarea.transition.duration'),
            border-color dt('textarea.transition.duration'),
            outline-color dt('textarea.transition.duration'),
            box-shadow dt('textarea.transition.duration');
        appearance: none;
        border-radius: dt('textarea.border.radius');
        outline-color: transparent;
        box-shadow: dt('textarea.shadow');
    }

    .p-textarea:enabled:hover {
        border-color: dt('textarea.hover.border.color');
    }

    .p-textarea:enabled:focus {
        border-color: dt('textarea.focus.border.color');
        box-shadow: dt('textarea.focus.ring.shadow');
        outline: dt('textarea.focus.ring.width') dt('textarea.focus.ring.style') dt('textarea.focus.ring.color');
        outline-offset: dt('textarea.focus.ring.offset');
    }

    .p-textarea.p-invalid {
        border-color: dt('textarea.invalid.border.color');
    }

    .p-textarea.p-variant-filled {
        background: dt('textarea.filled.background');
    }

    .p-textarea.p-variant-filled:enabled:hover {
        background: dt('textarea.filled.hover.background');
    }

    .p-textarea.p-variant-filled:enabled:focus {
        background: dt('textarea.filled.focus.background');
    }

    .p-textarea:disabled {
        opacity: 1;
        background: dt('textarea.disabled.background');
        color: dt('textarea.disabled.color');
    }

    .p-textarea::placeholder {
        color: dt('textarea.placeholder.color');
    }

    .p-textarea.p-invalid::placeholder {
        color: dt('textarea.invalid.placeholder.color');
    }

    .p-textarea-fluid {
        width: 100%;
    }

    .p-textarea-resizable {
        overflow: hidden;
        resize: none;
    }

    .p-textarea-sm {
        font-size: dt('textarea.sm.font.size');
        padding-block: dt('textarea.sm.padding.y');
        padding-inline: dt('textarea.sm.padding.x');
    }

    .p-textarea-lg {
        font-size: dt('textarea.lg.font.size');
        padding-block: dt('textarea.lg.padding.y');
        padding-inline: dt('textarea.lg.padding.x');
    }
`,Kt={root:function(e){var a=e.instance,o=e.props;return["p-textarea p-component",{"p-filled":a.$filled,"p-textarea-resizable ":o.autoResize,"p-textarea-sm p-inputfield-sm":o.size==="small","p-textarea-lg p-inputfield-lg":o.size==="large","p-invalid":a.$invalid,"p-variant-filled":a.$variant==="filled","p-textarea-fluid":a.$fluid}]}},Ft=H.extend({name:"textarea",style:qt,classes:Kt}),Ht={name:"BaseTextarea",extends:yt,props:{autoResize:Boolean},style:Ft,provide:function(){return{$pcTextarea:this,$parentInstance:this}}};function Q(t){"@babel/helpers - typeof";return Q=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},Q(t)}function Nt(t,e,a){return(e=Rt(e))in t?Object.defineProperty(t,e,{value:a,enumerable:!0,configurable:!0,writable:!0}):t[e]=a,t}function Rt(t){var e=Mt(t,"string");return Q(e)=="symbol"?e:e+""}function Mt(t,e){if(Q(t)!="object"||!t)return t;var a=t[Symbol.toPrimitive];if(a!==void 0){var o=a.call(t,e);if(Q(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var oe={name:"Textarea",extends:Ht,inheritAttrs:!1,observer:null,mounted:function(){var e=this;this.autoResize&&(this.observer=new ResizeObserver(function(){requestAnimationFrame(function(){e.resize()})}),this.observer.observe(this.$el))},updated:function(){this.autoResize&&this.resize()},beforeUnmount:function(){this.observer&&this.observer.disconnect()},methods:{resize:function(){if(this.$el.offsetParent){var e=this.$el.style.height,a=parseInt(e)||0,o=this.$el.scrollHeight,p=!a||o>a,i=a&&o<a;i?(this.$el.style.height="auto",this.$el.style.height="".concat(this.$el.scrollHeight,"px")):p&&(this.$el.style.height="".concat(o,"px"))}},onInput:function(e){this.autoResize&&this.resize(),this.writeValue(e.target.value,e)}},computed:{attrs:function(){return v(this.ptmi("root",{context:{filled:this.$filled,disabled:this.disabled}}),this.formField)},dataP:function(){return ie(Nt({invalid:this.$invalid,fluid:this.$fluid,filled:this.$variant==="filled"},this.size,this.size))}}},Wt=["value","name","disabled","aria-invalid","data-p"];function Zt(t,e,a,o,p,i){return b(),f("textarea",v({class:t.cx("root"),value:t.d_value,name:t.name,disabled:t.disabled,"aria-invalid":t.invalid||void 0,"data-p":i.dataP,onInput:e[0]||(e[0]=function(){return i.onInput&&i.onInput.apply(i,arguments)})},i.attrs),null,16,Wt)}oe.render=Zt;var Ne={name:"ChevronLeftIcon",extends:_e};function Gt(t){return Yt(t)||Xt(t)||Jt(t)||Qt()}function Qt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Jt(t,e){if(t){if(typeof t=="string")return ye(t,e);var a={}.toString.call(t).slice(8,-1);return a==="Object"&&t.constructor&&(a=t.constructor.name),a==="Map"||a==="Set"?Array.from(t):a==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(a)?ye(t,e):void 0}}function Xt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Yt(t){if(Array.isArray(t))return ye(t)}function ye(t,e){(e==null||e>t.length)&&(e=t.length);for(var a=0,o=Array(e);a<e;a++)o[a]=t[a];return o}function el(t,e,a,o,p,i){return b(),f("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Gt(e[0]||(e[0]=[n("path",{d:"M9.61296 13C9.50997 13.0005 9.40792 12.9804 9.3128 12.9409C9.21767 12.9014 9.13139 12.8433 9.05902 12.7701L3.83313 7.54416C3.68634 7.39718 3.60388 7.19795 3.60388 6.99022C3.60388 6.78249 3.68634 6.58325 3.83313 6.43628L9.05902 1.21039C9.20762 1.07192 9.40416 0.996539 9.60724 1.00012C9.81032 1.00371 10.0041 1.08597 10.1477 1.22959C10.2913 1.37322 10.3736 1.56698 10.3772 1.77005C10.3808 1.97313 10.3054 2.16968 10.1669 2.31827L5.49496 6.99022L10.1669 11.6622C10.3137 11.8091 10.3962 12.0084 10.3962 12.2161C10.3962 12.4238 10.3137 12.6231 10.1669 12.7701C10.0945 12.8433 10.0083 12.9014 9.91313 12.9409C9.81801 12.9804 9.71596 13.0005 9.61296 13Z",fill:"currentColor"},null,-1)])),16)}Ne.render=el;var Re={name:"ChevronRightIcon",extends:_e};function tl(t){return ol(t)||al(t)||nl(t)||ll()}function ll(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function nl(t,e){if(t){if(typeof t=="string")return he(t,e);var a={}.toString.call(t).slice(8,-1);return a==="Object"&&t.constructor&&(a=t.constructor.name),a==="Map"||a==="Set"?Array.from(t):a==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(a)?he(t,e):void 0}}function al(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function ol(t){if(Array.isArray(t))return he(t)}function he(t,e){(e==null||e>t.length)&&(e=t.length);for(var a=0,o=Array(e);a<e;a++)o[a]=t[a];return o}function rl(t,e,a,o,p,i){return b(),f("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),tl(e[0]||(e[0]=[n("path",{d:"M4.38708 13C4.28408 13.0005 4.18203 12.9804 4.08691 12.9409C3.99178 12.9014 3.9055 12.8433 3.83313 12.7701C3.68634 12.6231 3.60388 12.4238 3.60388 12.2161C3.60388 12.0084 3.68634 11.8091 3.83313 11.6622L8.50507 6.99022L3.83313 2.31827C3.69467 2.16968 3.61928 1.97313 3.62287 1.77005C3.62645 1.56698 3.70872 1.37322 3.85234 1.22959C3.99596 1.08597 4.18972 1.00371 4.3928 1.00012C4.59588 0.996539 4.79242 1.07192 4.94102 1.21039L10.1669 6.43628C10.3137 6.58325 10.3962 6.78249 10.3962 6.99022C10.3962 7.19795 10.3137 7.39718 10.1669 7.54416L4.94102 12.7701C4.86865 12.8433 4.78237 12.9014 4.68724 12.9409C4.59212 12.9804 4.49007 13.0005 4.38708 13Z",fill:"currentColor"},null,-1)])),16)}Re.render=rl;var il=`
    .p-tabview-tablist-container {
        position: relative;
    }

    .p-tabview-scrollable > .p-tabview-tablist-container {
        overflow: hidden;
    }

    .p-tabview-tablist-scroll-container {
        overflow-x: auto;
        overflow-y: hidden;
        scroll-behavior: smooth;
        scrollbar-width: none;
        overscroll-behavior: contain auto;
    }

    .p-tabview-tablist-scroll-container::-webkit-scrollbar {
        display: none;
    }

    .p-tabview-tablist {
        display: flex;
        margin: 0;
        padding: 0;
        list-style-type: none;
        flex: 1 1 auto;
        background: dt('tabview.tab.list.background');
        border: 1px solid dt('tabview.tab.list.border.color');
        border-width: 0 0 1px 0;
        position: relative;
    }

    .p-tabview-tab-header {
        cursor: pointer;
        user-select: none;
        display: flex;
        align-items: center;
        text-decoration: none;
        position: relative;
        overflow: hidden;
        border-style: solid;
        border-width: 0 0 1px 0;
        border-color: transparent transparent dt('tabview.tab.border.color') transparent;
        color: dt('tabview.tab.color');
        padding: 1rem 1.125rem;
        font-weight: 600;
        border-top-right-radius: dt('border.radius.md');
        border-top-left-radius: dt('border.radius.md');
        transition:
            color dt('tabview.transition.duration'),
            outline-color dt('tabview.transition.duration');
        margin: 0 0 -1px 0;
        outline-color: transparent;
    }

    .p-tabview-tablist-item:not(.p-disabled) .p-tabview-tab-header:focus-visible {
        outline: dt('focus.ring.width') dt('focus.ring.style') dt('focus.ring.color');
        outline-offset: -1px;
    }

    .p-tabview-tablist-item:not(.p-highlight):not(.p-disabled):hover > .p-tabview-tab-header {
        color: dt('tabview.tab.hover.color');
    }

    .p-tabview-tablist-item.p-highlight > .p-tabview-tab-header {
        color: dt('tabview.tab.active.color');
    }

    .p-tabview-tab-title {
        line-height: 1;
        white-space: nowrap;
    }

    .p-tabview-next-button,
    .p-tabview-prev-button {
        position: absolute;
        top: 0;
        margin: 0;
        padding: 0;
        z-index: 2;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: dt('tabview.nav.button.background');
        color: dt('tabview.nav.button.color');
        width: 2.5rem;
        border-radius: 0;
        outline-color: transparent;
        transition:
            color dt('tabview.transition.duration'),
            outline-color dt('tabview.transition.duration');
        box-shadow: dt('tabview.nav.button.shadow');
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-tabview-next-button:focus-visible,
    .p-tabview-prev-button:focus-visible {
        outline: dt('focus.ring.width') dt('focus.ring.style') dt('focus.ring.color');
        outline-offset: dt('focus.ring.offset');
    }

    .p-tabview-next-button:hover,
    .p-tabview-prev-button:hover {
        color: dt('tabview.nav.button.hover.color');
    }

    .p-tabview-prev-button {
        left: 0;
    }

    .p-tabview-next-button {
        right: 0;
    }

    .p-tabview-panels {
        background: dt('tabview.tab.panel.background');
        color: dt('tabview.tab.panel.color');
        padding: 0.875rem 1.125rem 1.125rem 1.125rem;
    }

    .p-tabview-ink-bar {
        z-index: 1;
        display: block;
        position: absolute;
        bottom: -1px;
        height: 1px;
        background: dt('tabview.tab.active.border.color');
        transition: 250ms cubic-bezier(0.35, 0, 0.25, 1);
    }
`,sl={root:function(e){var a=e.props;return["p-tabview p-component",{"p-tabview-scrollable":a.scrollable}]},navContainer:"p-tabview-tablist-container",prevButton:"p-tabview-prev-button",navContent:"p-tabview-tablist-scroll-container",nav:"p-tabview-tablist",tab:{header:function(e){var a=e.instance,o=e.tab,p=e.index;return["p-tabview-tablist-item",a.getTabProp(o,"headerClass"),{"p-tabview-tablist-item-active":a.d_activeIndex===p,"p-disabled":a.getTabProp(o,"disabled")}]},headerAction:"p-tabview-tab-header",headerTitle:"p-tabview-tab-title",content:function(e){var a=e.instance,o=e.tab;return["p-tabview-panel",a.getTabProp(o,"contentClass")]}},inkbar:"p-tabview-ink-bar",nextButton:"p-tabview-next-button",panelContainer:"p-tabview-panels"},dl=H.extend({name:"tabview",style:il,classes:sl}),ul={name:"BaseTabView",extends:Te,props:{activeIndex:{type:Number,default:0},lazy:{type:Boolean,default:!1},scrollable:{type:Boolean,default:!1},tabindex:{type:Number,default:0},selectOnFocus:{type:Boolean,default:!1},prevButtonProps:{type:null,default:null},nextButtonProps:{type:null,default:null},prevIcon:{type:String,default:void 0},nextIcon:{type:String,default:void 0}},style:dl,provide:function(){return{$pcTabs:void 0,$pcTabView:this,$parentInstance:this}}},Me={name:"TabView",extends:ul,inheritAttrs:!1,emits:["update:activeIndex","tab-change","tab-click"],data:function(){return{d_activeIndex:this.activeIndex,isPrevButtonDisabled:!0,isNextButtonDisabled:!1}},watch:{activeIndex:function(e){this.d_activeIndex=e,this.scrollInView({index:e})}},mounted:function(){console.warn("Deprecated since v4. Use Tabs component instead."),this.updateInkBar(),this.scrollable&&this.updateButtonState()},updated:function(){this.updateInkBar(),this.scrollable&&this.updateButtonState()},methods:{isTabPanel:function(e){return e.type.name==="TabPanel"},isTabActive:function(e){return this.d_activeIndex===e},getTabProp:function(e,a){return e.props?e.props[a]:void 0},getKey:function(e,a){return this.getTabProp(e,"header")||a},getTabHeaderActionId:function(e){return"".concat(this.$id,"_").concat(e,"_header_action")},getTabContentId:function(e){return"".concat(this.$id,"_").concat(e,"_content")},getTabPT:function(e,a,o){var p=this.tabs.length,i={props:e.props,parent:{instance:this,props:this.$props,state:this.$data},context:{index:o,count:p,first:o===0,last:o===p-1,active:this.isTabActive(o)}};return v(this.ptm("tabpanel.".concat(a),{tabpanel:i}),this.ptm("tabpanel.".concat(a),i),this.ptmo(this.getTabProp(e,"pt"),a,i))},onScroll:function(e){this.scrollable&&this.updateButtonState(),e.preventDefault()},onPrevButtonClick:function(){var e=this.$refs.content,a=Z(e),o=e.scrollLeft-a;e.scrollLeft=o<=0?0:o},onNextButtonClick:function(){var e=this.$refs.content,a=Z(e)-this.getVisibleButtonWidths(),o=e.scrollLeft+a,p=e.scrollWidth-a;e.scrollLeft=o>=p?p:o},onTabClick:function(e,a,o){this.changeActiveIndex(e,a,o),this.$emit("tab-click",{originalEvent:e,index:o})},onTabKeyDown:function(e,a,o){switch(e.code){case"ArrowLeft":this.onTabArrowLeftKey(e);break;case"ArrowRight":this.onTabArrowRightKey(e);break;case"Home":this.onTabHomeKey(e);break;case"End":this.onTabEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":case"Space":this.onTabEnterKey(e,a,o);break}},onTabArrowRightKey:function(e){var a=this.findNextHeaderAction(e.target.parentElement);a?this.changeFocusedTab(e,a):this.onTabHomeKey(e),e.preventDefault()},onTabArrowLeftKey:function(e){var a=this.findPrevHeaderAction(e.target.parentElement);a?this.changeFocusedTab(e,a):this.onTabEndKey(e),e.preventDefault()},onTabHomeKey:function(e){var a=this.findFirstHeaderAction();this.changeFocusedTab(e,a),e.preventDefault()},onTabEndKey:function(e){var a=this.findLastHeaderAction();this.changeFocusedTab(e,a),e.preventDefault()},onPageDownKey:function(e){this.scrollInView({index:this.$refs.nav.children.length-2}),e.preventDefault()},onPageUpKey:function(e){this.scrollInView({index:0}),e.preventDefault()},onTabEnterKey:function(e,a,o){this.changeActiveIndex(e,a,o),e.preventDefault()},findNextHeaderAction:function(e){var a=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,o=a?e:e.nextElementSibling;return o?le(o,"data-p-disabled")||le(o,"data-pc-section")==="inkbar"?this.findNextHeaderAction(o):ze(o,'[data-pc-section="headeraction"]'):null},findPrevHeaderAction:function(e){var a=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,o=a?e:e.previousElementSibling;return o?le(o,"data-p-disabled")||le(o,"data-pc-section")==="inkbar"?this.findPrevHeaderAction(o):ze(o,'[data-pc-section="headeraction"]'):null},findFirstHeaderAction:function(){return this.findNextHeaderAction(this.$refs.nav.firstElementChild,!0)},findLastHeaderAction:function(){return this.findPrevHeaderAction(this.$refs.nav.lastElementChild,!0)},changeActiveIndex:function(e,a,o){!this.getTabProp(a,"disabled")&&this.d_activeIndex!==o&&(this.d_activeIndex=o,this.$emit("update:activeIndex",o),this.$emit("tab-change",{originalEvent:e,index:o}),this.scrollInView({index:o}))},changeFocusedTab:function(e,a){if(a&&(dt(a),this.scrollInView({element:a}),this.selectOnFocus)){var o=parseInt(a.parentElement.dataset.pcIndex,10),p=this.tabs[o];this.changeActiveIndex(e,p,o)}},scrollInView:function(e){var a=e.element,o=e.index,p=o===void 0?-1:o,i=a||this.$refs.nav.children[p];i&&i.scrollIntoView&&i.scrollIntoView({block:"nearest"})},updateInkBar:function(){var e=this.$refs.nav.children[this.d_activeIndex];this.$refs.inkbar.style.width=Z(e)+"px",this.$refs.inkbar.style.left=Ue(e).left-Ue(this.$refs.nav).left+"px"},updateButtonState:function(){var e=this.$refs.content,a=e.scrollLeft,o=e.scrollWidth,p=Z(e);this.isPrevButtonDisabled=a===0,this.isNextButtonDisabled=parseInt(a)===o-p},getVisibleButtonWidths:function(){var e=this.$refs,a=e.prevBtn,o=e.nextBtn;return[a,o].reduce(function(p,i){return i?p+Z(i):p},0)}},computed:{tabs:function(){var e=this;return this.$slots.default().reduce(function(a,o){return e.isTabPanel(o)?a.push(o):o.children&&o.children instanceof Array&&o.children.forEach(function(p){e.isTabPanel(p)&&a.push(p)}),a},[])},prevButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.previous:void 0},nextButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.next:void 0}},directives:{ripple:re},components:{ChevronLeftIcon:Ne,ChevronRightIcon:Re}};function J(t){"@babel/helpers - typeof";return J=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},J(t)}function Ke(t,e){var a=Object.keys(t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);e&&(o=o.filter(function(p){return Object.getOwnPropertyDescriptor(t,p).enumerable})),a.push.apply(a,o)}return a}function C(t){for(var e=1;e<arguments.length;e++){var a=arguments[e]!=null?arguments[e]:{};e%2?Ke(Object(a),!0).forEach(function(o){pl(t,o,a[o])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(a)):Ke(Object(a)).forEach(function(o){Object.defineProperty(t,o,Object.getOwnPropertyDescriptor(a,o))})}return t}function pl(t,e,a){return(e=cl(e))in t?Object.defineProperty(t,e,{value:a,enumerable:!0,configurable:!0,writable:!0}):t[e]=a,t}function cl(t){var e=bl(t,"string");return J(e)=="symbol"?e:e+""}function bl(t,e){if(J(t)!="object"||!t)return t;var a=t[Symbol.toPrimitive];if(a!==void 0){var o=a.call(t,e);if(J(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var fl=["tabindex","aria-label"],gl=["data-p-active","data-p-disabled","data-pc-index"],vl=["id","tabindex","aria-disabled","aria-selected","aria-controls","onClick","onKeydown"],ml=["tabindex","aria-label"],yl=["id","aria-labelledby","data-pc-index","data-p-active"];function hl(t,e,a,o,p,i){var x=ke("ripple");return b(),f("div",v({class:t.cx("root"),role:"tablist"},t.ptmi("root")),[n("div",v({class:t.cx("navContainer")},t.ptm("navContainer")),[t.scrollable&&!p.isPrevButtonDisabled?z((b(),f("button",v({key:0,ref:"prevBtn",type:"button",class:t.cx("prevButton"),tabindex:t.tabindex,"aria-label":i.prevButtonAriaLabel,onClick:e[0]||(e[0]=function(){return i.onPrevButtonClick&&i.onPrevButtonClick.apply(i,arguments)})},C(C({},t.prevButtonProps),t.ptm("prevButton")),{"data-pc-group-section":"navbutton"}),[L(t.$slots,"previcon",{},function(){return[(b(),O(K(t.prevIcon?"span":"ChevronLeftIcon"),v({"aria-hidden":"true",class:t.prevIcon},t.ptm("prevIcon")),null,16,["class"]))]})],16,fl)),[[x]]):k("",!0),n("div",v({ref:"content",class:t.cx("navContent"),onScroll:e[1]||(e[1]=function(){return i.onScroll&&i.onScroll.apply(i,arguments)})},t.ptm("navContent")),[n("ul",v({ref:"nav",class:t.cx("nav")},t.ptm("nav")),[(b(!0),f(U,null,F(i.tabs,function(c,g){return b(),f("li",v({key:i.getKey(c,g),style:i.getTabProp(c,"headerStyle"),class:t.cx("tab.header",{tab:c,index:g}),role:"presentation"},{ref_for:!0},C(C(C({},i.getTabProp(c,"headerProps")),i.getTabPT(c,"root",g)),i.getTabPT(c,"header",g)),{"data-pc-name":"tabpanel","data-p-active":p.d_activeIndex===g,"data-p-disabled":i.getTabProp(c,"disabled"),"data-pc-index":g}),[z((b(),f("a",v({id:i.getTabHeaderActionId(g),class:t.cx("tab.headerAction"),tabindex:i.getTabProp(c,"disabled")||!i.isTabActive(g)?-1:t.tabindex,role:"tab","aria-disabled":i.getTabProp(c,"disabled"),"aria-selected":i.isTabActive(g),"aria-controls":i.getTabContentId(g),onClick:function(D){return i.onTabClick(D,c,g)},onKeydown:function(D){return i.onTabKeyDown(D,c,g)}},{ref_for:!0},C(C({},i.getTabProp(c,"headerActionProps")),i.getTabPT(c,"headerAction",g))),[c.props&&c.props.header?(b(),f("span",v({key:0,class:t.cx("tab.headerTitle")},{ref_for:!0},i.getTabPT(c,"headerTitle",g)),P(c.props.header),17)):k("",!0),c.children&&c.children.header?(b(),O(K(c.children.header),{key:1})):k("",!0)],16,vl)),[[x]])],16,gl)}),128)),n("li",v({ref:"inkbar",class:t.cx("inkbar"),role:"presentation","aria-hidden":"true"},t.ptm("inkbar")),null,16)],16)],16),t.scrollable&&!p.isNextButtonDisabled?z((b(),f("button",v({key:1,ref:"nextBtn",type:"button",class:t.cx("nextButton"),tabindex:t.tabindex,"aria-label":i.nextButtonAriaLabel,onClick:e[2]||(e[2]=function(){return i.onNextButtonClick&&i.onNextButtonClick.apply(i,arguments)})},C(C({},t.nextButtonProps),t.ptm("nextButton")),{"data-pc-group-section":"navbutton"}),[L(t.$slots,"nexticon",{},function(){return[(b(),O(K(t.nextIcon?"span":"ChevronRightIcon"),v({"aria-hidden":"true",class:t.nextIcon},t.ptm("nextIcon")),null,16,["class"]))]})],16,ml)),[[x]]):k("",!0)],16),n("div",v({class:t.cx("panelContainer")},t.ptm("panelContainer")),[(b(!0),f(U,null,F(i.tabs,function(c,g){return b(),f(U,{key:i.getKey(c,g)},[!t.lazy||i.isTabActive(g)?z((b(),f("div",v({key:0,id:i.getTabContentId(g),style:i.getTabProp(c,"contentStyle"),class:t.cx("tab.content",{tab:c}),role:"tabpanel","aria-labelledby":i.getTabHeaderActionId(g)},{ref_for:!0},C(C(C({},i.getTabProp(c,"contentProps")),i.getTabPT(c,"root",g)),i.getTabPT(c,"content",g)),{"data-pc-name":"tabpanel","data-pc-index":g,"data-p-active":p.d_activeIndex===g}),[(b(),O(K(c)))],16,yl)),[[Ve,t.lazy?!0:i.isTabActive(g)]]):k("",!0)],64)}),128))],16)],16)}Me.render=hl;var xl={root:function(e){var a=e.instance;return["p-tabpanel",{"p-tabpanel-active":a.active}]}},wl=H.extend({name:"tabpanel",classes:xl}),kl={name:"BaseTabPanel",extends:Te,props:{value:{type:[String,Number],default:void 0},as:{type:[String,Object],default:"DIV"},asChild:{type:Boolean,default:!1},header:null,headerStyle:null,headerClass:null,headerProps:null,headerActionProps:null,contentStyle:null,contentClass:null,contentProps:null,disabled:Boolean},style:wl,provide:function(){return{$pcTabPanel:this,$parentInstance:this}}},E={name:"TabPanel",extends:kl,inheritAttrs:!1,inject:["$pcTabs"],computed:{active:function(){var e;return ae((e=this.$pcTabs)===null||e===void 0?void 0:e.d_value,this.value)},id:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tabpanel_").concat(this.value)},ariaLabelledby:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tab_").concat(this.value)},attrs:function(){return v(this.a11yAttrs,this.ptmi("root",this.ptParams))},a11yAttrs:function(){var e;return{id:this.id,tabindex:(e=this.$pcTabs)===null||e===void 0?void 0:e.tabindex,role:"tabpanel","aria-labelledby":this.ariaLabelledby,"data-pc-name":"tabpanel","data-p-active":this.active}},ptParams:function(){return{context:{active:this.active}}}}};function Vl(t,e,a,o,p,i){var x,c;return i.$pcTabs?(b(),f(U,{key:1},[t.asChild?L(t.$slots,"default",{key:1,class:j(t.cx("root")),active:i.active,a11yAttrs:i.a11yAttrs}):(b(),f(U,{key:0},[!((x=i.$pcTabs)!==null&&x!==void 0&&x.lazy)||i.active?z((b(),O(K(t.as),v({key:0,class:t.cx("root")},i.attrs),{default:y(function(){return[L(t.$slots,"default")]}),_:3},16,["class"])),[[Ve,(c=i.$pcTabs)!==null&&c!==void 0&&c.lazy?!0:i.active]]):k("",!0)],64))],64)):L(t.$slots,"default",{key:0})}E.render=Vl;var _l=`
    .p-togglebutton {
        display: inline-flex;
        cursor: pointer;
        user-select: none;
        overflow: hidden;
        position: relative;
        color: dt('togglebutton.color');
        background: dt('togglebutton.background');
        border: 1px solid dt('togglebutton.border.color');
        padding: dt('togglebutton.padding');
        font-size: 1rem;
        font-family: inherit;
        font-feature-settings: inherit;
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
        border-radius: dt('togglebutton.border.radius');
        outline-color: transparent;
        font-weight: dt('togglebutton.font.weight');
    }

    .p-togglebutton-content {
        display: inline-flex;
        flex: 1 1 auto;
        align-items: center;
        justify-content: center;
        gap: dt('togglebutton.gap');
        padding: dt('togglebutton.content.padding');
        background: transparent;
        border-radius: dt('togglebutton.content.border.radius');
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover {
        background: dt('togglebutton.hover.background');
        color: dt('togglebutton.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked {
        background: dt('togglebutton.checked.background');
        border-color: dt('togglebutton.checked.border.color');
        color: dt('togglebutton.checked.color');
    }

    .p-togglebutton-checked .p-togglebutton-content {
        background: dt('togglebutton.content.checked.background');
        box-shadow: dt('togglebutton.content.checked.shadow');
    }

    .p-togglebutton:focus-visible {
        box-shadow: dt('togglebutton.focus.ring.shadow');
        outline: dt('togglebutton.focus.ring.width') dt('togglebutton.focus.ring.style') dt('togglebutton.focus.ring.color');
        outline-offset: dt('togglebutton.focus.ring.offset');
    }

    .p-togglebutton.p-invalid {
        border-color: dt('togglebutton.invalid.border.color');
    }

    .p-togglebutton:disabled {
        opacity: 1;
        cursor: default;
        background: dt('togglebutton.disabled.background');
        border-color: dt('togglebutton.disabled.border.color');
        color: dt('togglebutton.disabled.color');
    }

    .p-togglebutton-label,
    .p-togglebutton-icon {
        position: relative;
        transition: none;
    }

    .p-togglebutton-icon {
        color: dt('togglebutton.icon.color');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover .p-togglebutton-icon {
        color: dt('togglebutton.icon.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked .p-togglebutton-icon {
        color: dt('togglebutton.icon.checked.color');
    }

    .p-togglebutton:disabled .p-togglebutton-icon {
        color: dt('togglebutton.icon.disabled.color');
    }

    .p-togglebutton-sm {
        padding: dt('togglebutton.sm.padding');
        font-size: dt('togglebutton.sm.font.size');
    }

    .p-togglebutton-sm .p-togglebutton-content {
        padding: dt('togglebutton.content.sm.padding');
    }

    .p-togglebutton-lg {
        padding: dt('togglebutton.lg.padding');
        font-size: dt('togglebutton.lg.font.size');
    }

    .p-togglebutton-lg .p-togglebutton-content {
        padding: dt('togglebutton.content.lg.padding');
    }

    .p-togglebutton-fluid {
        width: 100%;
    }
`,Tl={root:function(e){var a=e.instance,o=e.props;return["p-togglebutton p-component",{"p-togglebutton-checked":a.active,"p-invalid":a.$invalid,"p-togglebutton-fluid":o.fluid,"p-togglebutton-sm p-inputfield-sm":o.size==="small","p-togglebutton-lg p-inputfield-lg":o.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},Pl=H.extend({name:"togglebutton",style:_l,classes:Tl}),Sl={name:"BaseToggleButton",extends:Fe,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:Pl,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}};function X(t){"@babel/helpers - typeof";return X=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},X(t)}function $l(t,e,a){return(e=Al(e))in t?Object.defineProperty(t,e,{value:a,enumerable:!0,configurable:!0,writable:!0}):t[e]=a,t}function Al(t){var e=Cl(t,"string");return X(e)=="symbol"?e:e+""}function Cl(t,e){if(X(t)!="object"||!t)return t;var a=t[Symbol.toPrimitive];if(a!==void 0){var o=a.call(t,e);if(X(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var We={name:"ToggleButton",extends:Sl,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(e){var a=e==="root"?this.ptmi:this.ptm;return a(e,{context:{active:this.active,disabled:this.disabled}})},onChange:function(e){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,e),this.$emit("change",e))},onBlur:function(e){var a,o;(a=(o=this.formField).onBlur)===null||a===void 0||a.call(o,e)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return Oe(this.onLabel)&&Oe(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "},dataP:function(){return ie($l({checked:this.active,invalid:this.$invalid},this.size,this.size))}},directives:{ripple:re}},Il=["tabindex","disabled","aria-pressed","aria-label","aria-labelledby","data-p-checked","data-p-disabled","data-p"],Bl=["data-p"];function Ll(t,e,a,o,p,i){var x=ke("ripple");return z((b(),f("button",v({type:"button",class:t.cx("root"),tabindex:t.tabindex,disabled:t.disabled,"aria-pressed":t.d_value,onClick:e[0]||(e[0]=function(){return i.onChange&&i.onChange.apply(i,arguments)}),onBlur:e[1]||(e[1]=function(){return i.onBlur&&i.onBlur.apply(i,arguments)})},i.getPTOptions("root"),{"aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"data-p-checked":i.active,"data-p-disabled":t.disabled,"data-p":i.dataP}),[n("span",v({class:t.cx("content")},i.getPTOptions("content"),{"data-p":i.dataP}),[L(t.$slots,"default",{},function(){return[L(t.$slots,"icon",{value:t.d_value,class:j(t.cx("icon"))},function(){return[t.onIcon||t.offIcon?(b(),f("span",v({key:0,class:[t.cx("icon"),t.d_value?t.onIcon:t.offIcon]},i.getPTOptions("icon")),null,16)):k("",!0)]}),n("span",v({class:t.cx("label")},i.getPTOptions("label")),P(i.label),17)]})],16,Bl)],16,Il)),[[x]])}We.render=Ll;var Dl=`
    .p-selectbutton {
        display: inline-flex;
        user-select: none;
        vertical-align: bottom;
        outline-color: transparent;
        border-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton .p-togglebutton {
        border-radius: 0;
        border-width: 1px 1px 1px 0;
    }

    .p-selectbutton .p-togglebutton:focus-visible {
        position: relative;
        z-index: 1;
    }

    .p-selectbutton .p-togglebutton:first-child {
        border-inline-start-width: 1px;
        border-start-start-radius: dt('selectbutton.border.radius');
        border-end-start-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton .p-togglebutton:last-child {
        border-start-end-radius: dt('selectbutton.border.radius');
        border-end-end-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton.p-invalid {
        outline: 1px solid dt('selectbutton.invalid.border.color');
        outline-offset: 0;
    }

    .p-selectbutton-fluid {
        width: 100%;
    }

    .p-selectbutton-fluid .p-togglebutton {
        flex: 1 1 0;
    }
`,Ul={root:function(e){var a=e.props,o=e.instance;return["p-selectbutton p-component",{"p-invalid":o.$invalid,"p-selectbutton-fluid":a.fluid}]}},zl=H.extend({name:"selectbutton",style:Dl,classes:Ul}),Ol={name:"BaseSelectButton",extends:Fe,props:{options:Array,optionLabel:null,optionValue:null,optionDisabled:null,multiple:Boolean,allowEmpty:{type:Boolean,default:!0},dataKey:null,ariaLabelledby:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:zl,provide:function(){return{$pcSelectButton:this,$parentInstance:this}}};function El(t,e){var a=typeof Symbol<"u"&&t[Symbol.iterator]||t["@@iterator"];if(!a){if(Array.isArray(t)||(a=Ze(t))||e){a&&(t=a);var o=0,p=function(){};return{s:p,n:function(){return o>=t.length?{done:!0}:{done:!1,value:t[o++]}},e:function(S){throw S},f:p}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var i,x=!0,c=!1;return{s:function(){a=a.call(t)},n:function(){var S=a.next();return x=S.done,S},e:function(S){c=!0,i=S},f:function(){try{x||a.return==null||a.return()}finally{if(c)throw i}}}}function jl(t){return Fl(t)||Kl(t)||Ze(t)||ql()}function ql(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Ze(t,e){if(t){if(typeof t=="string")return xe(t,e);var a={}.toString.call(t).slice(8,-1);return a==="Object"&&t.constructor&&(a=t.constructor.name),a==="Map"||a==="Set"?Array.from(t):a==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(a)?xe(t,e):void 0}}function Kl(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Fl(t){if(Array.isArray(t))return xe(t)}function xe(t,e){(e==null||e>t.length)&&(e=t.length);for(var a=0,o=Array(e);a<e;a++)o[a]=t[a];return o}var we={name:"SelectButton",extends:Ol,inheritAttrs:!1,emits:["change"],methods:{getOptionLabel:function(e){return this.optionLabel?ne(e,this.optionLabel):e},getOptionValue:function(e){return this.optionValue?ne(e,this.optionValue):e},getOptionRenderKey:function(e){return this.dataKey?ne(e,this.dataKey):this.getOptionLabel(e)},isOptionDisabled:function(e){return this.optionDisabled?ne(e,this.optionDisabled):!1},isOptionReadonly:function(e){if(this.allowEmpty)return!1;var a=this.isSelected(e);return this.multiple?a&&this.d_value.length===1:a},onOptionSelect:function(e,a,o){var p=this;if(!(this.disabled||this.isOptionDisabled(a)||this.isOptionReadonly(a))){var i=this.isSelected(a),x=this.getOptionValue(a),c;if(this.multiple)if(i){if(c=this.d_value.filter(function(g){return!ae(g,x,p.equalityKey)}),!this.allowEmpty&&c.length===0)return}else c=this.d_value?[].concat(jl(this.d_value),[x]):[x];else{if(i&&!this.allowEmpty)return;c=i?null:x}this.writeValue(c,e),this.$emit("change",{originalEvent:e,value:c})}},isSelected:function(e){var a=!1,o=this.getOptionValue(e);if(this.multiple){if(this.d_value){var p=El(this.d_value),i;try{for(p.s();!(i=p.n()).done;){var x=i.value;if(ae(x,o,this.equalityKey)){a=!0;break}}}catch(c){p.e(c)}finally{p.f()}}}else a=ae(this.d_value,o,this.equalityKey);return a}},computed:{equalityKey:function(){return this.optionValue?null:this.dataKey},dataP:function(){return ie({invalid:this.$invalid})}},directives:{ripple:re},components:{ToggleButton:We}},Hl=["aria-labelledby","data-p"];function Nl(t,e,a,o,p,i){var x=ut("ToggleButton");return b(),f("div",v({class:t.cx("root"),role:"group","aria-labelledby":t.ariaLabelledby},t.ptmi("root"),{"data-p":i.dataP}),[(b(!0),f(U,null,F(t.options,function(c,g){return b(),O(x,{key:i.getOptionRenderKey(c),modelValue:i.isSelected(c),onLabel:i.getOptionLabel(c),offLabel:i.getOptionLabel(c),disabled:t.disabled||i.isOptionDisabled(c),unstyled:t.unstyled,size:t.size,readonly:i.isOptionReadonly(c),onChange:function(D){return i.onOptionSelect(D,c,g)},pt:t.ptm("pcToggleButton")},pt({_:2},[t.$slots.option?{name:"default",fn:y(function(){return[L(t.$slots,"option",{option:c,index:g},function(){return[n("span",v({ref_for:!0},t.ptm("pcToggleButton").label),P(i.getOptionLabel(c)),17)]})]}),key:"0"}:void 0]),1032,["modelValue","onLabel","offLabel","disabled","unstyled","size","readonly","onChange","pt"])}),128))],16,Hl)}we.render=Nl;const Rl={class:"p-4 flex flex-col gap-4"},Ml={key:0,class:"flex justify-center"},Wl={key:1},Zl={class:"flex flex-col gap-6"},Gl={class:"flex flex-col gap-4"},Ql={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},Jl={class:"flex flex-col gap-2"},Xl={class:"flex flex-col gap-2"},Yl={class:"flex flex-col gap-2"},en={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},tn={class:"flex items-center gap-2"},ln=["for"],nn={class:"flex flex-col gap-2"},an={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},on=["for"],rn={class:"flex flex-col gap-4"},sn={class:"flex flex-col gap-2"},dn={class:"flex flex-col gap-4"},un={class:"flex items-center gap-2 p-3 bg-gray-800 rounded border border-gray-700"},pn={key:0,class:"flex flex-col gap-2"},cn={class:"flex items-center gap-2"},bn={key:0,class:"flex flex-col gap-6 mt-4"},fn={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},gn={class:"flex flex-col gap-2"},vn={class:"flex flex-col gap-2"},mn={class:"flex flex-col gap-2"},yn={class:"flex flex-col gap-2"},hn={class:"border-t border-gray-700 pt-4"},xn={class:"flex items-center gap-2 mb-3"},wn={key:0,class:"ml-8 mb-4"},kn={class:"flex flex-col gap-2"},Vn={class:"grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 pt-4"},_n={class:"flex flex-col gap-2"},Tn={class:"flex flex-col gap-2"},Pn={class:"flex flex-col gap-3 border border-green-600/50 rounded bg-green-900/10 p-4"},Sn={class:"flex items-center gap-2"},$n={key:0,class:"ml-8"},An={key:1,class:"text-gray-400 italic"},Cn={class:"flex flex-col gap-6"},In={class:"flex items-center gap-2"},Bn={key:0,class:"flex flex-col gap-4"},Ln={class:"flex flex-col gap-2"},Dn={class:"flex flex-col gap-2"},Un={class:"flex flex-col gap-2 border-t border-gray-700 pt-4 mt-2"},zn={class:"flex flex-col gap-2"},On={class:"flex items-center gap-2"},En={key:0,class:"flex flex-col gap-4"},jn={class:"flex flex-col gap-2"},qn={class:"flex flex-col gap-2"},Kn={class:"flex items-center gap-2"},Fn={key:0,class:"flex flex-col gap-4"},Hn={class:"flex flex-col gap-2"},Nn={class:"flex items-center gap-2"},Rn={key:0,class:"flex flex-col gap-4"},Mn={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},Wn={class:"flex flex-col gap-2"},Zn={class:"flex flex-col gap-2"},Gn={class:"flex flex-col gap-2"},Qn={class:"flex flex-col gap-2"},Jn={class:"flex flex-col gap-2"},Xn={class:"flex flex-col gap-2"},Yn={class:"flex flex-col gap-6"},ea={class:"flex items-center gap-2"},ta={key:0,class:"flex flex-col gap-6"},la={class:"bg-gray-800 p-4 rounded border border-gray-700 mt-4"},na={key:0,class:"grid grid-cols-1 md:grid-cols-2 gap-4 text-sm"},aa={class:"flex justify-between border-b border-gray-700 py-2"},oa={class:"font-mono"},ra={class:"flex justify-between border-b border-gray-700 py-2"},ia={class:"flex justify-between border-b border-gray-700 py-2"},sa={class:"font-mono text-lg"},da={class:"flex justify-between border-b border-gray-700 py-2"},ua={class:"flex justify-between border-b border-gray-700 py-2"},pa={class:"font-mono"},ca={key:1,class:"text-center py-4 text-gray-500"},ba={class:"flex flex-col gap-6"},fa={class:"flex flex-col gap-4"},ga={class:"flex flex-col gap-2"},va={class:"flex items-center gap-2 mt-2"},ma={class:"flex items-center gap-2"},ya={key:0,class:"flex flex-col gap-4"},ha={class:"bg-yellow-900/20 border border-yellow-600/50 p-3 rounded text-yellow-200 text-sm flex items-start gap-2"},xa={class:"grid grid-cols-1 md:grid-cols-2 gap-6"},wa={class:"flex flex-col gap-2"},ka={class:"flex flex-col gap-2"},Va={class:"grid grid-cols-1 xl:grid-cols-2 gap-6"},_a={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},Ta={class:"flex items-center justify-between bg-gray-900/50 p-3 rounded"},Pa={class:"font-mono"},Sa={class:"text-right"},$a={class:"font-mono text-green-400"},Aa={key:0,class:"bg-blue-900/20 border border-blue-600/50 p-3 rounded mt-2 flex flex-col gap-2"},Ca={class:"flex flex-col gap-2 mt-2 border-t border-gray-700 pt-2"},Ia={class:"flex gap-2"},Ba={class:"flex justify-between items-center mt-1"},La={class:"flex items-center gap-2"},Da={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},Ua={class:"flex flex-col gap-2 mb-2"},za={class:"flex items-center justify-between"},Oa={class:"flex items-center gap-2"},Ea={key:0,class:"grid grid-cols-2 gap-2 text-sm bg-gray-900/30 p-2 rounded"},ja={class:"flex flex-col"},qa={class:"flex flex-col"},Ka={class:"col-span-2 flex items-center gap-2 mt-1"},Fa={class:"flex gap-2"},Ha={class:"mt-2 max-h-40 overflow-y-auto"},Na={class:"truncate"},Ra={class:"flex gap-1"},Ma={class:"border-t border-gray-700 pt-3 mt-2"},Wa={class:"flex items-center gap-2 mb-2"},Za={key:0,class:"flex flex-col gap-2"},Ga={class:"flex flex-col gap-1"},Qa={class:"flex flex-col gap-1"},Ja={class:"flex flex-col gap-1"},Xa={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3 xl:col-span-2"},Ya={class:"flex gap-4"},eo={class:"flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4 sticky bottom-0 bg-gray-900/90 backdrop-blur p-4 z-10"},to={class:"flex flex-col gap-4"},lo={class:"flex flex-col gap-2"},no={class:"flex flex-col gap-2"},ao={key:0,class:"text-red-500"},oo={class:"flex flex-col gap-4"},mo={__name:"Config",setup(t){const e=h({idm:{host:"",port:502,circuits:["A"],zones:[]},metrics:{url:""},web:{write_enabled:!1},logging:{interval:60,realtime_mode:!1},mqtt:{enabled:!1,broker:"",port:1883,username:"",topic_prefix:"idm/heatpump",qos:0,use_tls:!1,tls_ca_cert:"",publish_interval:60,ha_discovery_enabled:!1,ha_discovery_prefix:"homeassistant"},network_security:{enabled:!1,whitelist:[],blacklist:[]},signal:{enabled:!1,cli_path:"signal-cli",sender:"",recipients:[]},telegram:{enabled:!1,bot_token:"",chat_ids:[]},discord:{enabled:!1,webhook_url:""},email:{enabled:!1,smtp_server:"",smtp_port:587,username:"",sender:"",recipients:[]},webdav:{enabled:!1,url:"",username:""},ai:{enabled:!1,sensitivity:3,model:"rolling"},updates:{enabled:!1,interval_hours:12,mode:"apply",target:"all",channel:"latest"},backup:{enabled:!1,interval:24,retention:10,auto_upload:!1}}),a=h(!1),o=h(""),p=h(""),i=h(""),x=h(""),c=h(""),g=h(""),S=h(""),D=h(""),Y=h(""),ee=h(""),N=h({}),Ge=h({}),B=h(null),Pe=h(!1),se=h(!1),Se=h(""),$e=h(!0),de=h(!1),m=ct(),te=bt();let ue=null;const pe=ft(()=>o.value&&p.value&&o.value!==p.value);gt(()=>{ue&&clearInterval(ue)});const Ae=h([]),Ce=h(!1),ce=h(!1),Ie=h(!1),R=h(null),be=h(null),M=h(!1),W=h(""),fe=h(!1),ge=h(!1);vt(async()=>{try{const u=await _.get("/api/config");e.value=u.data,e.value.network_security&&(g.value=(e.value.network_security.whitelist||[]).join(`
`),S.value=(e.value.network_security.blacklist||[]).join(`
`)),e.value.signal&&(D.value=(e.value.signal.recipients||[]).join(`
`)),e.value.telegram&&(Y.value=(e.value.telegram.chat_ids||[]).join(", ")),e.value.email&&(ee.value=(e.value.email.recipients||[]).join(", "));try{const l=await _.get("/api/health");Se.value=l.data.client_ip||"Unbekannt"}catch(l){console.error("Failed to get client IP",l)}ve(),Be(),Le(),ue=setInterval(Le,1e4)}catch{m.add({severity:"error",summary:"Fehler",detail:"Konfiguration konnte nicht geladen werden",life:3e3})}finally{$e.value=!1}});const Qe=async()=>{try{const u=await _.post("/api/signal/test",{message:"Signal Test vom IDM Metrics Collector"});u.data.success?m.add({severity:"success",summary:"Erfolg",detail:u.data.message,life:3e3}):m.add({severity:"error",summary:"Fehler",detail:u.data.error||"Signal Test fehlgeschlagen",life:3e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||u.message,life:5e3})}},Be=async()=>{Pe.value=!0;try{const[u,l]=await Promise.all([_.get("/api/check-update",{params:{channel:e.value.updates?.channel||"latest"}}),_.get("/api/signal/status")]);N.value=u.data,Ge.value=l.data}catch(u){console.error("Status load failed",u)}finally{Pe.value=!1}},Je=async()=>{se.value=!0;try{const u=await _.get("/api/check-update",{params:{channel:e.value.updates.channel}});N.value=u.data,u.data.update_available?m.add({severity:"info",summary:"Update verfügbar",detail:`Version ${u.data.latest_version} ist verfügbar.`,life:5e3}):m.add({severity:"success",summary:"System aktuell",detail:"Keine Updates gefunden.",life:3e3})}catch{m.add({severity:"error",summary:"Fehler",detail:"Update-Prüfung fehlgeschlagen",life:3e3})}finally{se.value=!1}},Xe=()=>{a.value=!1,De()},Le=async()=>{try{const u=await _.get("/api/ai/status");B.value=u.data}catch(u){console.error("Failed to load AI status",u)}},De=async()=>{de.value=!0;try{const u={idm_host:e.value.idm.host,idm_port:e.value.idm.port,circuits:e.value.idm.circuits,zones:e.value.idm.zones,metrics_url:e.value.metrics.url,write_enabled:e.value.web.write_enabled,logging_interval:e.value.logging.interval,realtime_mode:e.value.logging.realtime_mode,mqtt_enabled:e.value.mqtt?.enabled||!1,mqtt_broker:e.value.mqtt?.broker||"",mqtt_port:e.value.mqtt?.port||1883,mqtt_username:e.value.mqtt?.username||"",mqtt_password:i.value||void 0,mqtt_topic_prefix:e.value.mqtt?.topic_prefix||"idm/heatpump",mqtt_qos:e.value.mqtt?.qos||0,mqtt_use_tls:e.value.mqtt?.use_tls||!1,mqtt_tls_ca_cert:e.value.mqtt?.tls_ca_cert||"",mqtt_publish_interval:e.value.mqtt?.publish_interval||60,mqtt_ha_discovery_enabled:e.value.mqtt?.ha_discovery_enabled||!1,mqtt_ha_discovery_prefix:e.value.mqtt?.ha_discovery_prefix||"homeassistant",network_security_enabled:e.value.network_security?.enabled||!1,network_security_whitelist:g.value,network_security_blacklist:S.value,signal_enabled:e.value.signal?.enabled||!1,signal_sender:e.value.signal?.sender||"",signal_cli_path:e.value.signal?.cli_path||"signal-cli",signal_recipients:D.value,telegram_enabled:e.value.telegram?.enabled||!1,telegram_bot_token:e.value.telegram?.bot_token||"",telegram_chat_ids:Y.value,discord_enabled:e.value.discord?.enabled||!1,discord_webhook_url:e.value.discord?.webhook_url||"",email_enabled:e.value.email?.enabled||!1,email_smtp_server:e.value.email?.smtp_server||"",email_smtp_port:e.value.email?.smtp_port||587,email_username:e.value.email?.username||"",email_password:x.value||void 0,email_sender:e.value.email?.sender||"",email_recipients:ee.value,webdav_enabled:e.value.webdav?.enabled||!1,webdav_url:e.value.webdav?.url||"",webdav_username:e.value.webdav?.username||"",webdav_password:c.value||void 0,ai_enabled:e.value.ai?.enabled||!1,ai_sensitivity:e.value.ai?.sensitivity||3,ai_model:e.value.ai?.model||"rolling",updates_enabled:e.value.updates?.enabled||!1,updates_interval_hours:e.value.updates?.interval_hours||12,updates_mode:e.value.updates?.mode||"apply",updates_target:e.value.updates?.target||"all",updates_channel:e.value.updates?.channel||"latest",backup_enabled:e.value.backup?.enabled||!1,backup_interval:e.value.backup?.interval||24,backup_retention:e.value.backup?.retention||10,backup_auto_upload:e.value.backup?.auto_upload||!1,new_password:o.value||void 0},l=await _.post("/api/config",u);m.add({severity:"success",summary:"Erfolg",detail:l.data.message||"Einstellungen erfolgreich gespeichert",life:3e3}),o.value="",p.value="",i.value="",c.value=""}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||u.message,life:5e3})}finally{de.value=!1}},Ye=()=>{te.require({message:"Bist du sicher, dass du den Dienst neu starten möchtest?",header:"Bestätigung",icon:"pi pi-exclamation-triangle",accept:async()=>{try{const u=await _.post("/api/restart");m.add({severity:"info",summary:"Neustart",detail:u.data.message,life:3e3})}catch{m.add({severity:"error",summary:"Fehler",detail:"Neustart fehlgeschlagen",life:3e3})}}})},ve=async()=>{Ce.value=!0;try{const u=await _.get("/api/backup/list");Ae.value=u.data.backups||[]}catch{m.add({severity:"error",summary:"Fehler",detail:"Backups konnten nicht geladen werden",life:3e3})}finally{Ce.value=!1}},et=async()=>{ce.value=!0;try{const u=await _.post("/api/backup/create");u.data.success?(m.add({severity:"success",summary:"Erfolg",detail:`Backup erstellt: ${u.data.filename}`,life:3e3}),ve()):m.add({severity:"error",summary:"Fehler",detail:u.data.error,life:3e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Backup Erstellung fehlgeschlagen",life:3e3})}finally{ce.value=!1}},tt=async u=>{try{const l=await _.get(`/api/backup/download/${u}`,{responseType:"blob"}),r=window.URL.createObjectURL(new Blob([l.data])),A=document.createElement("a");A.href=r,A.setAttribute("download",u),document.body.appendChild(A),A.click(),A.remove(),m.add({severity:"success",summary:"Erfolg",detail:"Backup heruntergeladen",life:2e3})}catch{m.add({severity:"error",summary:"Fehler",detail:"Backup Download fehlgeschlagen",life:3e3})}},lt=async u=>{try{m.add({severity:"info",summary:"Info",detail:"Upload gestartet...",life:2e3});const l=await _.post(`/api/backup/upload/${u}`);l.data.success?m.add({severity:"success",summary:"Erfolg",detail:"Backup erfolgreich hochgeladen",life:3e3}):m.add({severity:"error",summary:"Fehler",detail:l.data.error,life:5e3})}catch(l){m.add({severity:"error",summary:"Fehler",detail:l.response?.data?.error||"Upload fehlgeschlagen",life:5e3})}},nt=u=>{te.require({message:`Backup "${u}" löschen?`,header:"Backup Löschen",icon:"pi pi-trash",acceptClass:"p-button-danger",accept:async()=>{try{await _.delete(`/api/backup/delete/${u}`),m.add({severity:"success",summary:"Erfolg",detail:"Backup gelöscht",life:2e3}),ve()}catch{m.add({severity:"error",summary:"Fehler",detail:"Backup löschen fehlgeschlagen",life:3e3})}}})},at=u=>{const l=u.target.files[0];R.value=l},ot=async()=>{R.value&&te.require({message:"Konfiguration aus hochgeladener Datei wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!",header:"Aus Datei Wiederherstellen",icon:"pi pi-exclamation-triangle",acceptClass:"p-button-warning",accept:async()=>{Ie.value=!0;try{const u=new FormData;u.append("file",R.value),u.append("restore_secrets","false");const l=await _.post("/api/backup/restore",u,{headers:{"Content-Type":"multipart/form-data"}});l.data.success?(m.add({severity:"success",summary:"Erfolg",detail:l.data.message,life:5e3}),R.value=null,be.value&&(be.value.value=""),setTimeout(()=>location.reload(),2e3)):m.add({severity:"error",summary:"Fehler",detail:l.data.error,life:5e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Wiederherstellung fehlgeschlagen",life:5e3})}finally{Ie.value=!1}}})},rt=async()=>{if(W.value==="DELETE"){fe.value=!0;try{const u=await _.post("/api/database/delete");u.data.success?(m.add({severity:"success",summary:"Erfolg",detail:u.data.message,life:5e3}),M.value=!1,W.value=""):m.add({severity:"error",summary:"Fehler",detail:u.data.error,life:5e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Datenbank löschen fehlgeschlagen",life:5e3})}finally{fe.value=!1}}},it=()=>{te.require({message:"Update wirklich durchführen? Der Dienst wird neu gestartet.",header:"Update Bestätigung",icon:"pi pi-refresh",acceptClass:"p-button-info",accept:async()=>{ge.value=!0;try{const u=await _.post("/api/perform-update");u.data.success?(m.add({severity:"success",summary:"Update gestartet",detail:"System wird aktualisiert...",life:5e3}),setTimeout(Be,15e3)):m.add({severity:"error",summary:"Fehler",detail:u.data.error,life:5e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Update fehlgeschlagen",life:5e3})}finally{ge.value=!1}}})};return(u,l)=>(b(),f("div",Rl,[l[137]||(l[137]=n("h1",{class:"text-2xl font-bold mb-4"},"Konfiguration",-1)),$e.value?(b(),f("div",Ml,[...l[60]||(l[60]=[n("i",{class:"pi pi-spin pi-spinner text-4xl"},null,-1)])])):(b(),f("div",Wl,[d(s(Me),null,{default:y(()=>[d(s(E),{header:"Verbindung"},{default:y(()=>[n("div",Zl,[d(s(I),{legend:"IDM Wärmepumpe",toggleable:!0},{default:y(()=>[n("div",Gl,[n("div",Ql,[n("div",Jl,[l[61]||(l[61]=n("label",null,"Host / IP",-1)),d(s(w),{modelValue:e.value.idm.host,"onUpdate:modelValue":l[0]||(l[0]=r=>e.value.idm.host=r),class:"w-full"},null,8,["modelValue"])]),n("div",Xl,[l[62]||(l[62]=n("label",null,"Port",-1)),d(s(q),{modelValue:e.value.idm.port,"onUpdate:modelValue":l[1]||(l[1]=r=>e.value.idm.port=r),useGrouping:!1,class:"w-full"},null,8,["modelValue"])])]),n("div",Yl,[l[64]||(l[64]=n("label",{class:"font-bold"},"Aktivierte Heizkreise",-1)),n("div",en,[n("div",tn,[d(s(V),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":l[2]||(l[2]=r=>e.value.idm.circuits=r),inputId:"circuitA",value:"A",disabled:""},null,8,["modelValue"]),l[63]||(l[63]=n("label",{for:"circuitA",class:"opacity-50"},"Heizkreis A (Fest)",-1))]),(b(),f(U,null,F(["B","C","D","E","F","G"],r=>n("div",{key:r,class:"flex items-center gap-2"},[d(s(V),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":l[3]||(l[3]=A=>e.value.idm.circuits=A),inputId:"circuit"+r,value:r},null,8,["modelValue","inputId","value"]),n("label",{for:"circuit"+r},"Heizkreis "+P(r),9,ln)])),64))])]),n("div",nn,[l[65]||(l[65]=n("label",{class:"font-bold"},"Zonenmodule",-1)),n("div",an,[(b(),f(U,null,F(10,r=>n("div",{key:r,class:"flex items-center gap-2"},[d(s(V),{modelValue:e.value.idm.zones,"onUpdate:modelValue":l[4]||(l[4]=A=>e.value.idm.zones=A),inputId:"zone"+(r-1),value:r-1},null,8,["modelValue","inputId","value"]),n("label",{for:"zone"+(r-1)},"Zone "+P(r),9,on)])),64))])])])]),_:1}),d(s(I),{legend:"Datenbank (VictoriaMetrics)",toggleable:!0},{default:y(()=>[n("div",rn,[n("div",sn,[l[66]||(l[66]=n("label",null,"Write URL",-1)),d(s(w),{modelValue:e.value.metrics.url,"onUpdate:modelValue":l[5]||(l[5]=r=>e.value.metrics.url=r),class:"w-full"},null,8,["modelValue"]),l[67]||(l[67]=n("small",{class:"text-gray-300"},"Standard: http://victoriametrics:8428/write",-1))])])]),_:1}),d(s(I),{legend:"Datenerfassung",toggleable:!0},{default:y(()=>[n("div",dn,[n("div",un,[d(s(V),{modelValue:e.value.logging.realtime_mode,"onUpdate:modelValue":l[6]||(l[6]=r=>e.value.logging.realtime_mode=r),binary:"",inputId:"realtime_mode"},null,8,["modelValue"]),l[68]||(l[68]=n("div",{class:"flex flex-col"},[n("label",{for:"realtime_mode",class:"font-bold cursor-pointer"},"Echtzeit-Modus"),n("span",{class:"text-sm text-gray-400"},"Aktualisierung im Sekundentakt (Hohe Last)")],-1))]),e.value.logging.realtime_mode?k("",!0):(b(),f("div",pn,[l[69]||(l[69]=n("label",null,"Abfrage-Intervall (Sekunden)",-1)),d(s(q),{modelValue:e.value.logging.interval,"onUpdate:modelValue":l[7]||(l[7]=r=>e.value.logging.interval=r),min:1,max:3600,useGrouping:!1,class:"w-full md:w-1/2"},null,8,["modelValue"]),l[70]||(l[70]=n("small",{class:"text-gray-400"},"Standard: 60 Sekunden",-1))]))])]),_:1})])]),_:1}),d(s(E),{header:"MQTT & Integration"},{default:y(()=>[d(s(I),{legend:"MQTT Publishing",toggleable:!1},{legend:y(()=>[n("div",cn,[d(s(V),{modelValue:e.value.mqtt.enabled,"onUpdate:modelValue":l[8]||(l[8]=r=>e.value.mqtt.enabled=r),binary:"",inputId:"mqtt_enabled"},null,8,["modelValue"]),l[71]||(l[71]=n("span",{class:"font-bold text-lg"},"MQTT Aktivieren",-1))])]),default:y(()=>[e.value.mqtt.enabled?(b(),f("div",bn,[n("div",fn,[n("div",gn,[l[72]||(l[72]=n("label",null,"Broker Adresse",-1)),d(s(w),{modelValue:e.value.mqtt.broker,"onUpdate:modelValue":l[9]||(l[9]=r=>e.value.mqtt.broker=r),placeholder:"mqtt.example.com",class:"w-full"},null,8,["modelValue"])]),n("div",vn,[l[73]||(l[73]=n("label",null,"Port",-1)),d(s(q),{modelValue:e.value.mqtt.port,"onUpdate:modelValue":l[10]||(l[10]=r=>e.value.mqtt.port=r),useGrouping:!1,min:1,max:65535,class:"w-full"},null,8,["modelValue"])]),n("div",mn,[l[74]||(l[74]=n("label",null,"Benutzername",-1)),d(s(w),{modelValue:e.value.mqtt.username,"onUpdate:modelValue":l[11]||(l[11]=r=>e.value.mqtt.username=r),placeholder:"Optional",class:"w-full"},null,8,["modelValue"])]),n("div",yn,[l[75]||(l[75]=n("label",null,"Passwort",-1)),d(s(w),{modelValue:i.value,"onUpdate:modelValue":l[12]||(l[12]=r=>i.value=r),type:"password",placeholder:"••••••",class:"w-full"},null,8,["modelValue"])])]),n("div",hn,[n("div",xn,[d(s(V),{modelValue:e.value.mqtt.use_tls,"onUpdate:modelValue":l[13]||(l[13]=r=>e.value.mqtt.use_tls=r),binary:"",inputId:"mqtt_tls"},null,8,["modelValue"]),l[76]||(l[76]=n("label",{for:"mqtt_tls",class:"font-bold cursor-pointer"},"TLS/SSL Verschlüsselung",-1))]),e.value.mqtt.use_tls?(b(),f("div",wn,[n("div",kn,[l[77]||(l[77]=n("label",{class:"text-sm"},"CA-Zertifikat Pfad (optional)",-1)),d(s(w),{modelValue:e.value.mqtt.tls_ca_cert,"onUpdate:modelValue":l[14]||(l[14]=r=>e.value.mqtt.tls_ca_cert=r),placeholder:"/path/to/ca.crt",class:"w-full"},null,8,["modelValue"]),l[78]||(l[78]=n("small",{class:"text-gray-400"},"Für selbst-signierte Zertifikate. Leer lassen für System-CA.",-1))])])):k("",!0)]),n("div",Vn,[n("div",_n,[l[79]||(l[79]=n("label",null,"Topic Präfix",-1)),d(s(w),{modelValue:e.value.mqtt.topic_prefix,"onUpdate:modelValue":l[15]||(l[15]=r=>e.value.mqtt.topic_prefix=r),class:"w-full"},null,8,["modelValue"])]),n("div",Tn,[l[80]||(l[80]=n("label",null,"QoS Level",-1)),d(s(we),{modelValue:e.value.mqtt.qos,"onUpdate:modelValue":l[16]||(l[16]=r=>e.value.mqtt.qos=r),options:[0,1,2],"aria-labelledby":"basic",class:"w-full"},null,8,["modelValue"])])]),n("div",Pn,[n("div",Sn,[d(s(V),{modelValue:e.value.mqtt.ha_discovery_enabled,"onUpdate:modelValue":l[17]||(l[17]=r=>e.value.mqtt.ha_discovery_enabled=r),binary:"",inputId:"ha_discovery"},null,8,["modelValue"]),l[81]||(l[81]=n("label",{for:"ha_discovery",class:"font-bold text-green-400 cursor-pointer"},"Home Assistant Auto-Discovery",-1))]),e.value.mqtt.ha_discovery_enabled?(b(),f("div",$n,[l[82]||(l[82]=n("label",{class:"text-sm"},"Discovery Präfix",-1)),d(s(w),{modelValue:e.value.mqtt.ha_discovery_prefix,"onUpdate:modelValue":l[18]||(l[18]=r=>e.value.mqtt.ha_discovery_prefix=r),class:"w-full mt-1"},null,8,["modelValue"])])):k("",!0)])])):(b(),f("div",An," Aktivieren Sie MQTT, um Daten an Broker wie Mosquitto oder Home Assistant zu senden. "))]),_:1})]),_:1}),d(s(E),{header:"Benachrichtigungen"},{default:y(()=>[n("div",Cn,[d(s(I),{legend:"Signal Messenger",toggleable:!0},{legend:y(()=>[n("div",In,[d(s(V),{modelValue:e.value.signal.enabled,"onUpdate:modelValue":l[19]||(l[19]=r=>e.value.signal.enabled=r),binary:""},null,8,["modelValue"]),l[83]||(l[83]=n("span",{class:"font-bold"},"Signal",-1))])]),default:y(()=>[e.value.signal.enabled?(b(),f("div",Bn,[n("div",Ln,[l[84]||(l[84]=n("label",null,"Sender Nummer",-1)),d(s(w),{modelValue:e.value.signal.sender,"onUpdate:modelValue":l[20]||(l[20]=r=>e.value.signal.sender=r),placeholder:"+49...",class:"w-full md:w-1/2"},null,8,["modelValue"])]),n("div",Dn,[l[85]||(l[85]=n("label",null,"Empfänger (Pro Zeile eine Nummer)",-1)),d(s(oe),{modelValue:D.value,"onUpdate:modelValue":l[21]||(l[21]=r=>D.value=r),rows:"3",class:"w-full font-mono"},null,8,["modelValue"])]),n("div",Un,[l[88]||(l[88]=n("label",{class:"text-sm font-bold"},"Erweitert",-1)),n("div",zn,[l[86]||(l[86]=n("label",{class:"text-xs"},"Signal CLI Pfad",-1)),d(s(w),{modelValue:e.value.signal.cli_path,"onUpdate:modelValue":l[22]||(l[22]=r=>e.value.signal.cli_path=r),placeholder:"signal-cli",class:"w-full md:w-1/2"},null,8,["modelValue"]),l[87]||(l[87]=n("small",{class:"text-gray-400"},"Standard: signal-cli (im PATH)",-1))])]),d(s(T),{label:"Testnachricht senden",icon:"pi pi-send",severity:"success",outlined:"",onClick:Qe,class:"w-full md:w-auto self-start"})])):k("",!0)]),_:1}),d(s(I),{legend:"Telegram",toggleable:!0},{legend:y(()=>[n("div",On,[d(s(V),{modelValue:e.value.telegram.enabled,"onUpdate:modelValue":l[23]||(l[23]=r=>e.value.telegram.enabled=r),binary:""},null,8,["modelValue"]),l[89]||(l[89]=n("span",{class:"font-bold"},"Telegram",-1))])]),default:y(()=>[e.value.telegram.enabled?(b(),f("div",En,[n("div",jn,[l[90]||(l[90]=n("label",null,"Bot Token",-1)),d(s(w),{modelValue:e.value.telegram.bot_token,"onUpdate:modelValue":l[24]||(l[24]=r=>e.value.telegram.bot_token=r),type:"password",class:"w-full md:w-1/2"},null,8,["modelValue"])]),n("div",qn,[l[91]||(l[91]=n("label",null,"Chat IDs (Kommagetrennt)",-1)),d(s(w),{modelValue:Y.value,"onUpdate:modelValue":l[25]||(l[25]=r=>Y.value=r),class:"w-full md:w-1/2"},null,8,["modelValue"])])])):k("",!0)]),_:1}),d(s(I),{legend:"Discord",toggleable:!0},{legend:y(()=>[n("div",Kn,[d(s(V),{modelValue:e.value.discord.enabled,"onUpdate:modelValue":l[26]||(l[26]=r=>e.value.discord.enabled=r),binary:""},null,8,["modelValue"]),l[92]||(l[92]=n("span",{class:"font-bold"},"Discord",-1))])]),default:y(()=>[e.value.discord.enabled?(b(),f("div",Fn,[n("div",Hn,[l[93]||(l[93]=n("label",null,"Webhook URL",-1)),d(s(w),{modelValue:e.value.discord.webhook_url,"onUpdate:modelValue":l[27]||(l[27]=r=>e.value.discord.webhook_url=r),type:"password",class:"w-full"},null,8,["modelValue"])])])):k("",!0)]),_:1}),d(s(I),{legend:"E-Mail",toggleable:!0},{legend:y(()=>[n("div",Nn,[d(s(V),{modelValue:e.value.email.enabled,"onUpdate:modelValue":l[28]||(l[28]=r=>e.value.email.enabled=r),binary:""},null,8,["modelValue"]),l[94]||(l[94]=n("span",{class:"font-bold"},"E-Mail",-1))])]),default:y(()=>[e.value.email.enabled?(b(),f("div",Rn,[n("div",Mn,[n("div",Wn,[l[95]||(l[95]=n("label",null,"SMTP Server",-1)),d(s(w),{modelValue:e.value.email.smtp_server,"onUpdate:modelValue":l[29]||(l[29]=r=>e.value.email.smtp_server=r),class:"w-full"},null,8,["modelValue"])]),n("div",Zn,[l[96]||(l[96]=n("label",null,"Port",-1)),d(s(q),{modelValue:e.value.email.smtp_port,"onUpdate:modelValue":l[30]||(l[30]=r=>e.value.email.smtp_port=r),useGrouping:!1,class:"w-full"},null,8,["modelValue"])]),n("div",Gn,[l[97]||(l[97]=n("label",null,"Benutzername",-1)),d(s(w),{modelValue:e.value.email.username,"onUpdate:modelValue":l[31]||(l[31]=r=>e.value.email.username=r),class:"w-full"},null,8,["modelValue"])]),n("div",Qn,[l[98]||(l[98]=n("label",null,"Passwort",-1)),d(s(w),{modelValue:x.value,"onUpdate:modelValue":l[32]||(l[32]=r=>x.value=r),type:"password",class:"w-full"},null,8,["modelValue"])]),n("div",Jn,[l[99]||(l[99]=n("label",null,"Absender Adresse",-1)),d(s(w),{modelValue:e.value.email.sender,"onUpdate:modelValue":l[33]||(l[33]=r=>e.value.email.sender=r),class:"w-full"},null,8,["modelValue"])])]),n("div",Xn,[l[100]||(l[100]=n("label",null,"Empfänger (Kommagetrennt)",-1)),d(s(w),{modelValue:ee.value,"onUpdate:modelValue":l[34]||(l[34]=r=>ee.value=r),class:"w-full"},null,8,["modelValue"])])])):k("",!0)]),_:1})])]),_:1}),d(s(E),{header:"KI-Analyse"},{default:y(()=>[n("div",Yn,[d(s(I),{legend:"KI & Anomalieerkennung",toggleable:!0},{legend:y(()=>[n("div",ea,[d(s(V),{modelValue:e.value.ai.enabled,"onUpdate:modelValue":l[35]||(l[35]=r=>e.value.ai.enabled=r),binary:""},null,8,["modelValue"]),l[101]||(l[101]=n("span",{class:"font-bold"},"KI-Analyse Status anzeigen",-1))])]),default:y(()=>[e.value.ai.enabled?(b(),f("div",ta,[l[110]||(l[110]=n("div",{class:"bg-blue-900/20 border border-blue-600/50 p-4 rounded flex items-start gap-3"},[n("i",{class:"pi pi-info-circle text-blue-400 text-xl mt-1"}),n("div",{class:"text-sm text-blue-200"},[$(" Die Anomalieerkennung läuft nun als eigenständiger "),n("strong",null,"ml-service"),$(' Container. Er nutzt die "HalfSpaceTrees" Methode (via Python '),n("code",null,"river"),$("), um kontinuierlich aus dem Datenstrom zu lernen. ")])],-1)),n("div",la,[l[108]||(l[108]=n("h4",{class:"font-bold text-lg mb-2 flex items-center gap-2"},[n("i",{class:"pi pi-chart-line"}),$(" Service Status ")],-1)),B.value?(b(),f("div",na,[n("div",aa,[l[102]||(l[102]=n("span",{class:"text-gray-400"},"Service:",-1)),n("span",oa,P(B.value.service||"Unbekannt"),1)]),n("div",ra,[l[103]||(l[103]=n("span",{class:"text-gray-400"},"Status:",-1)),n("span",{class:j(["font-bold",B.value.online?"text-green-400":"text-red-400"])},P(B.value.online?"Online":"Offline / Keine Daten"),3)]),n("div",ia,[l[104]||(l[104]=n("span",{class:"text-gray-400"},"Letzter Score:",-1)),n("span",sa,P(B.value.score?B.value.score.toFixed(4):"0.0000"),1)]),n("div",da,[l[105]||(l[105]=n("span",{class:"text-gray-400"},"Aktuelle Anomalie:",-1)),n("span",{class:j(["font-bold",B.value.is_anomaly?"text-red-500":"text-green-500"])},P(B.value.is_anomaly?"JA":"NEIN"),3)]),n("div",ua,[l[106]||(l[106]=n("span",{class:"text-gray-400"},"Letztes Update:",-1)),n("span",pa,P(B.value.last_update?new Date(B.value.last_update*1e3).toLocaleString():"-"),1)])])):(b(),f("div",ca,[...l[107]||(l[107]=[n("i",{class:"pi pi-spin pi-spinner mr-2"},null,-1),$(" Lade Status... ",-1)])])),l[109]||(l[109]=n("div",{class:"mt-4 text-xs text-gray-500 text-center"},[$(" Hinweis: Alarme können über Grafana konfiguriert werden (Metrik: "),n("code",null,"idm_anomaly_flag"),$("). ")],-1))])])):k("",!0)]),_:1})])]),_:1}),d(s(E),{header:"Sicherheit"},{default:y(()=>[n("div",ba,[d(s(I),{legend:"Webzugriff",toggleable:!0},{default:y(()=>[n("div",fa,[n("div",ga,[l[111]||(l[111]=n("label",null,"Admin Passwort",-1)),d(s(T),{label:"Passwort ändern",icon:"pi pi-key",severity:"secondary",outlined:"",class:"w-full md:w-auto self-start",onClick:l[36]||(l[36]=r=>a.value=!0)})]),n("div",va,[d(s(V),{modelValue:e.value.web.write_enabled,"onUpdate:modelValue":l[37]||(l[37]=r=>e.value.web.write_enabled=r),binary:"",inputId:"write_access"},null,8,["modelValue"]),l[112]||(l[112]=n("div",{class:"flex flex-col"},[n("label",{for:"write_access",class:"font-bold cursor-pointer"},"Schreibzugriff erlauben"),n("span",{class:"text-sm text-gray-400"},"Erforderlich für manuelle Steuerung und Zeitpläne")],-1))])])]),_:1}),d(s(I),{legend:"Netzwerk Firewall",toggleable:!0},{legend:y(()=>[n("div",ma,[d(s(V),{modelValue:e.value.network_security.enabled,"onUpdate:modelValue":l[38]||(l[38]=r=>e.value.network_security.enabled=r),binary:""},null,8,["modelValue"]),l[113]||(l[113]=n("span",{class:"font-bold"},"IP Whitelist/Blacklist",-1))])]),default:y(()=>[e.value.network_security.enabled?(b(),f("div",ya,[n("div",ha,[l[116]||(l[116]=n("i",{class:"pi pi-exclamation-triangle mt-0.5"},null,-1)),n("span",null,[l[114]||(l[114]=$("Deine IP ist ",-1)),n("strong",null,P(Se.value),1),l[115]||(l[115]=$(". Füge diese zur Whitelist hinzu, sonst sperrst du dich aus!",-1))])]),n("div",xa,[n("div",wa,[l[117]||(l[117]=n("label",{class:"font-bold text-green-400"},"Whitelist (Erlaubt)",-1)),d(s(oe),{modelValue:g.value,"onUpdate:modelValue":l[39]||(l[39]=r=>g.value=r),rows:"5",class:"w-full font-mono text-sm",placeholder:"192.168.1.0/24"},null,8,["modelValue"])]),n("div",ka,[l[118]||(l[118]=n("label",{class:"font-bold text-red-400"},"Blacklist (Blockiert)",-1)),d(s(oe),{modelValue:S.value,"onUpdate:modelValue":l[40]||(l[40]=r=>S.value=r),rows:"5",class:"w-full font-mono text-sm",placeholder:"1.2.3.4"},null,8,["modelValue"])])])])):k("",!0)]),_:1})])]),_:1}),d(s(E),{header:"System & Wartung"},{default:y(()=>[n("div",Va,[n("div",_a,[l[124]||(l[124]=n("h3",{class:"font-bold text-lg flex items-center gap-2"},[n("i",{class:"pi pi-refresh"}),$(" Update Status ")],-1)),n("div",Ta,[n("div",null,[l[119]||(l[119]=n("div",{class:"text-sm text-gray-400"},"Installierte Version",-1)),n("div",Pa,P(N.value.current_version||"v0.0.0"),1)]),n("div",Sa,[l[120]||(l[120]=n("div",{class:"text-sm text-gray-400"},"Verfügbare Version",-1)),n("div",$a,P(N.value.latest_version||"Checking..."),1)])]),N.value.update_available?(b(),f("div",Aa,[l[121]||(l[121]=n("div",{class:"flex items-center gap-2 text-blue-300 text-sm"},[n("i",{class:"pi pi-info-circle"}),n("span",null,"Neue Version verfügbar!")],-1)),d(s(T),{label:"Jetzt aktualisieren",icon:"pi pi-download",severity:"info",size:"small",onClick:it,loading:ge.value},null,8,["loading"])])):k("",!0),n("div",Ca,[l[123]||(l[123]=n("label",{class:"text-sm font-bold"},"Update Kanal",-1)),n("div",Ia,[d(s(we),{modelValue:e.value.updates.channel,"onUpdate:modelValue":l[41]||(l[41]=r=>e.value.updates.channel=r),options:["latest","beta","release"],allowEmpty:!1,class:"w-full"},null,8,["modelValue"])]),n("div",Ba,[n("div",La,[d(s(V),{modelValue:e.value.updates.enabled,"onUpdate:modelValue":l[42]||(l[42]=r=>e.value.updates.enabled=r),binary:"",inputId:"auto_updates"},null,8,["modelValue"]),l[122]||(l[122]=n("label",{for:"auto_updates",class:"text-sm"},"Auto-Updates",-1))]),d(s(T),{label:"Suche Updates",icon:"pi pi-search",size:"small",onClick:Je,loading:se.value},null,8,["loading"])])])]),n("div",Da,[l[132]||(l[132]=n("h3",{class:"font-bold text-lg flex items-center gap-2"},[n("i",{class:"pi pi-database"}),$(" Backup ")],-1)),n("div",Ua,[n("div",za,[n("div",Oa,[d(s(V),{modelValue:e.value.backup.enabled,"onUpdate:modelValue":l[43]||(l[43]=r=>e.value.backup.enabled=r),binary:"",inputId:"auto_backup"},null,8,["modelValue"]),l[125]||(l[125]=n("label",{for:"auto_backup",class:"font-bold text-sm"},"Automatisches Backup",-1))])]),e.value.backup.enabled?(b(),f("div",Ea,[n("div",ja,[l[126]||(l[126]=n("label",{class:"text-xs text-gray-400"},"Intervall (Std)",-1)),d(s(q),{modelValue:e.value.backup.interval,"onUpdate:modelValue":l[44]||(l[44]=r=>e.value.backup.interval=r),min:1,max:168,class:"p-inputtext-sm"},null,8,["modelValue"])]),n("div",qa,[l[127]||(l[127]=n("label",{class:"text-xs text-gray-400"},"Behalten (Anzahl)",-1)),d(s(q),{modelValue:e.value.backup.retention,"onUpdate:modelValue":l[45]||(l[45]=r=>e.value.backup.retention=r),min:1,max:50,class:"p-inputtext-sm"},null,8,["modelValue"])]),n("div",Ka,[d(s(V),{modelValue:e.value.backup.auto_upload,"onUpdate:modelValue":l[46]||(l[46]=r=>e.value.backup.auto_upload=r),binary:"",inputId:"backup_upload",disabled:!e.value.webdav.enabled},null,8,["modelValue","disabled"]),n("label",{for:"backup_upload",class:j(["text-xs",{"opacity-50":!e.value.webdav.enabled}])},"Automatisch in Cloud hochladen",2)])])):k("",!0)]),n("div",Fa,[d(s(T),{label:"Backup erstellen",icon:"pi pi-download",size:"small",onClick:et,loading:ce.value},null,8,["loading"]),d(s(T),{label:"Backup hochladen",icon:"pi pi-upload",size:"small",severity:"secondary",onClick:l[47]||(l[47]=r=>u.$refs.fileInput.click())}),n("input",{type:"file",ref_key:"fileInput",ref:be,class:"hidden",onChange:at,accept:".zip"},null,544)]),R.value?(b(),O(s(T),{key:0,label:"Wiederherstellen starten",severity:"warning",class:"w-full mt-2",onClick:ot})):k("",!0),n("div",Ha,[(b(!0),f(U,null,F(Ae.value,r=>(b(),f("div",{key:r.filename,class:"flex justify-between items-center p-2 hover:bg-gray-700 rounded text-sm border-b border-gray-700 last:border-0"},[n("span",Na,P(r.filename),1),n("div",Ra,[d(s(T),{icon:"pi pi-cloud-upload",text:"",size:"small",onClick:A=>lt(r.filename),title:"Upload to WebDAV"},null,8,["onClick"]),d(s(T),{icon:"pi pi-download",text:"",size:"small",onClick:A=>tt(r.filename)},null,8,["onClick"]),d(s(T),{icon:"pi pi-trash",text:"",severity:"danger",size:"small",onClick:A=>nt(r.filename)},null,8,["onClick"])])]))),128))]),n("div",Ma,[n("div",Wa,[d(s(V),{modelValue:e.value.webdav.enabled,"onUpdate:modelValue":l[48]||(l[48]=r=>e.value.webdav.enabled=r),binary:"",inputId:"webdav_enabled"},null,8,["modelValue"]),l[128]||(l[128]=n("label",{for:"webdav_enabled",class:"font-bold cursor-pointer"},"Cloud Backup (WebDAV/Nextcloud)",-1))]),e.value.webdav.enabled?(b(),f("div",Za,[n("div",Ga,[l[129]||(l[129]=n("label",{class:"text-xs"},"URL",-1)),d(s(w),{modelValue:e.value.webdav.url,"onUpdate:modelValue":l[49]||(l[49]=r=>e.value.webdav.url=r),placeholder:"https://cloud.example.com/remote.php/dav/files/user/",class:"p-inputtext-sm w-full"},null,8,["modelValue"])]),n("div",Qa,[l[130]||(l[130]=n("label",{class:"text-xs"},"Benutzername",-1)),d(s(w),{modelValue:e.value.webdav.username,"onUpdate:modelValue":l[50]||(l[50]=r=>e.value.webdav.username=r),class:"p-inputtext-sm w-full"},null,8,["modelValue"])]),n("div",Ja,[l[131]||(l[131]=n("label",{class:"text-xs"},"Passwort",-1)),d(s(w),{modelValue:c.value,"onUpdate:modelValue":l[51]||(l[51]=r=>c.value=r),type:"password",class:"p-inputtext-sm w-full"},null,8,["modelValue"])])])):k("",!0)])]),n("div",Xa,[l[133]||(l[133]=n("h3",{class:"font-bold text-lg flex items-center gap-2 text-red-400"},[n("i",{class:"pi pi-power-off"}),$(" Danger Zone ")],-1)),n("div",Ya,[d(s(T),{label:"Dienst neu starten",icon:"pi pi-refresh",severity:"warning",onClick:Ye}),d(s(T),{label:"Datenbank löschen",icon:"pi pi-trash",severity:"danger",onClick:l[52]||(l[52]=r=>M.value=!0)})])])])]),_:1})]),_:1})])),n("div",eo,[d(s(T),{label:"Speichern",icon:"pi pi-save",onClick:De,loading:de.value,size:"large",severity:"primary"},null,8,["loading"])]),d(s(Ee),{visible:a.value,"onUpdate:visible":l[56]||(l[56]=r=>a.value=r),modal:"",header:"Passwort ändern",style:{width:"400px"}},{footer:y(()=>[d(s(T),{label:"Abbrechen",text:"",onClick:l[55]||(l[55]=r=>a.value=!1)}),d(s(T),{label:"Speichern",onClick:Xe,disabled:!o.value||!p.value||pe.value},null,8,["disabled"])]),default:y(()=>[n("div",to,[n("div",lo,[l[134]||(l[134]=n("label",null,"Neues Passwort",-1)),d(s(w),{modelValue:o.value,"onUpdate:modelValue":l[53]||(l[53]=r=>o.value=r),type:"password",class:"w-full"},null,8,["modelValue"])]),n("div",no,[l[135]||(l[135]=n("label",null,"Bestätigen",-1)),d(s(w),{modelValue:p.value,"onUpdate:modelValue":l[54]||(l[54]=r=>p.value=r),type:"password",class:j(["w-full",{"p-invalid":pe.value}])},null,8,["modelValue","class"]),pe.value?(b(),f("small",ao,"Passwörter stimmen nicht überein")):k("",!0)])])]),_:1},8,["visible"]),d(s(Ee),{visible:M.value,"onUpdate:visible":l[59]||(l[59]=r=>M.value=r),modal:"",header:"Datenbank löschen",style:{width:"450px"}},{footer:y(()=>[d(s(T),{label:"Abbrechen",text:"",onClick:l[58]||(l[58]=r=>M.value=!1)}),d(s(T),{label:"Alles löschen",severity:"danger",onClick:rt,disabled:W.value!=="DELETE",loading:fe.value},null,8,["disabled","loading"])]),default:y(()=>[n("div",oo,[l[136]||(l[136]=n("div",{class:"flex items-start gap-3"},[n("i",{class:"pi pi-exclamation-triangle text-red-500 text-2xl"}),n("div",{class:"flex flex-col gap-2"},[n("span",{class:"font-bold text-lg"},"Bist du dir absolut sicher?"),n("p",{class:"text-gray-300"},[$(" Diese Aktion löscht "),n("span",{class:"font-bold text-red-400"},"ALLE"),$(" Daten dauerhaft aus der Datenbank. ")])])],-1)),d(s(w),{modelValue:W.value,"onUpdate:modelValue":l[57]||(l[57]=r=>W.value=r),placeholder:"Tippe DELETE",class:"w-full"},null,8,["modelValue"])])]),_:1},8,["visible"]),d(s(ht)),d(s(xt))]))}};export{mo as default};
