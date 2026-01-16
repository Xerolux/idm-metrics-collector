import{a as f,o as b,f as a,m as v,B as H,l as ke,b as d,p as L,h as k,q as z,t as P,n as j,g as O,s as q,w as y,ag as Ve,T as st,aa as Z,ah as Ue,D as dt,A as ze,ai as ne,F as U,x as F,X as ae,z as Oe,a5 as le,k as ut,a6 as ct,r as h,v as pt,U as bt,c as ft,L as gt,K as vt,y as V,d as s,j as S}from"./index-CFwYSV0y.js";import{a as mt,s as _}from"./index-DA6iLukj.js";import{b as _e,R as re,a as Te,f as ie,s as T}from"./index-DNG_n9rH.js";import{a as yt,b as Fe,s as w}from"./index-viDAH1y4.js";import{s as K}from"./index-D-WMYjaL.js";import{s as ht}from"./index-C_OQCerN.js";import{s as xt}from"./index-BuV9gZhv.js";import{s as Ee}from"./index-CgdfGV4p.js";import"./index-BI9smfcs.js";import"./index-D0ulg186.js";var He={name:"PlusIcon",extends:_e};function wt(t){return Tt(t)||_t(t)||Vt(t)||kt()}function kt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Vt(t,e){if(t){if(typeof t=="string")return me(t,e);var l={}.toString.call(t).slice(8,-1);return l==="Object"&&t.constructor&&(l=t.constructor.name),l==="Map"||l==="Set"?Array.from(t):l==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(l)?me(t,e):void 0}}function _t(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Tt(t){if(Array.isArray(t))return me(t)}function me(t,e){(e==null||e>t.length)&&(e=t.length);for(var l=0,o=Array(e);l<e;l++)o[l]=t[l];return o}function Pt(t,e,l,o,c,i){return b(),f("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),wt(e[0]||(e[0]=[a("path",{d:"M7.67742 6.32258V0.677419C7.67742 0.497757 7.60605 0.325452 7.47901 0.198411C7.35197 0.0713707 7.17966 0 7 0C6.82034 0 6.64803 0.0713707 6.52099 0.198411C6.39395 0.325452 6.32258 0.497757 6.32258 0.677419V6.32258H0.677419C0.497757 6.32258 0.325452 6.39395 0.198411 6.52099C0.0713707 6.64803 0 6.82034 0 7C0 7.17966 0.0713707 7.35197 0.198411 7.47901C0.325452 7.60605 0.497757 7.67742 0.677419 7.67742H6.32258V13.3226C6.32492 13.5015 6.39704 13.6725 6.52358 13.799C6.65012 13.9255 6.82106 13.9977 7 14C7.17966 14 7.35197 13.9286 7.47901 13.8016C7.60605 13.6745 7.67742 13.5022 7.67742 13.3226V7.67742H13.3226C13.5022 7.67742 13.6745 7.60605 13.8016 7.47901C13.9286 7.35197 14 7.17966 14 7C13.9977 6.82106 13.9255 6.65012 13.799 6.52358C13.6725 6.39704 13.5015 6.32492 13.3226 6.32258H7.67742Z",fill:"currentColor"},null,-1)])),16)}He.render=Pt;var $t=`
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
`,St={root:function(e){var l=e.props;return["p-fieldset p-component",{"p-fieldset-toggleable":l.toggleable}]},legend:"p-fieldset-legend",legendLabel:"p-fieldset-legend-label",toggleButton:"p-fieldset-toggle-button",toggleIcon:"p-fieldset-toggle-icon",contentContainer:"p-fieldset-content-container",contentWrapper:"p-fieldset-content-wrapper",content:"p-fieldset-content"},At=H.extend({name:"fieldset",style:$t,classes:St}),Ct={name:"BaseFieldset",extends:Te,props:{legend:String,toggleable:Boolean,collapsed:Boolean,toggleButtonProps:{type:null,default:null}},style:At,provide:function(){return{$pcFieldset:this,$parentInstance:this}}},I={name:"Fieldset",extends:Ct,inheritAttrs:!1,emits:["update:collapsed","toggle"],data:function(){return{d_collapsed:this.collapsed}},watch:{collapsed:function(e){this.d_collapsed=e}},methods:{toggle:function(e){this.d_collapsed=!this.d_collapsed,this.$emit("update:collapsed",this.d_collapsed),this.$emit("toggle",{originalEvent:e,value:this.d_collapsed})},onKeyDown:function(e){(e.code==="Enter"||e.code==="NumpadEnter"||e.code==="Space")&&(this.toggle(e),e.preventDefault())}},computed:{buttonAriaLabel:function(){return this.toggleButtonProps&&this.toggleButtonProps.ariaLabel?this.toggleButtonProps.ariaLabel:this.legend},dataP:function(){return ie({toggleable:this.toggleable})}},directives:{ripple:re},components:{PlusIcon:He,MinusIcon:mt}};function G(t){"@babel/helpers - typeof";return G=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},G(t)}function je(t,e){var l=Object.keys(t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);e&&(o=o.filter(function(c){return Object.getOwnPropertyDescriptor(t,c).enumerable})),l.push.apply(l,o)}return l}function Ke(t){for(var e=1;e<arguments.length;e++){var l=arguments[e]!=null?arguments[e]:{};e%2?je(Object(l),!0).forEach(function(o){It(t,o,l[o])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(l)):je(Object(l)).forEach(function(o){Object.defineProperty(t,o,Object.getOwnPropertyDescriptor(l,o))})}return t}function It(t,e,l){return(e=Bt(e))in t?Object.defineProperty(t,e,{value:l,enumerable:!0,configurable:!0,writable:!0}):t[e]=l,t}function Bt(t){var e=Lt(t,"string");return G(e)=="symbol"?e:e+""}function Lt(t,e){if(G(t)!="object"||!t)return t;var l=t[Symbol.toPrimitive];if(l!==void 0){var o=l.call(t,e);if(G(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var Dt=["data-p"],Ut=["data-p"],zt=["id"],Ot=["id","aria-controls","aria-expanded","aria-label"],Et=["id","aria-labelledby"];function jt(t,e,l,o,c,i){var x=ke("ripple");return b(),f("fieldset",v({class:t.cx("root"),"data-p":i.dataP},t.ptmi("root")),[a("legend",v({class:t.cx("legend"),"data-p":i.dataP},t.ptm("legend")),[L(t.$slots,"legend",{toggleCallback:i.toggle},function(){return[t.toggleable?k("",!0):(b(),f("span",v({key:0,id:t.$id+"_header",class:t.cx("legendLabel")},t.ptm("legendLabel")),P(t.legend),17,zt)),t.toggleable?z((b(),f("button",v({key:1,id:t.$id+"_header",type:"button","aria-controls":t.$id+"_content","aria-expanded":!c.d_collapsed,"aria-label":i.buttonAriaLabel,class:t.cx("toggleButton"),onClick:e[0]||(e[0]=function(){return i.toggle&&i.toggle.apply(i,arguments)}),onKeydown:e[1]||(e[1]=function(){return i.onKeyDown&&i.onKeyDown.apply(i,arguments)})},Ke(Ke({},t.toggleButtonProps),t.ptm("toggleButton"))),[L(t.$slots,t.$slots.toggleicon?"toggleicon":"togglericon",{collapsed:c.d_collapsed,class:j(t.cx("toggleIcon"))},function(){return[(b(),O(q(c.d_collapsed?"PlusIcon":"MinusIcon"),v({class:t.cx("toggleIcon")},t.ptm("toggleIcon")),null,16,["class"]))]}),a("span",v({class:t.cx("legendLabel")},t.ptm("legendLabel")),P(t.legend),17)],16,Ot)),[[x]]):k("",!0)]})],16,Ut),d(st,v({name:"p-collapsible"},t.ptm("transition")),{default:y(function(){return[z(a("div",v({id:t.$id+"_content",class:t.cx("contentContainer"),role:"region","aria-labelledby":t.$id+"_header"},t.ptm("contentContainer")),[a("div",v({class:t.cx("contentWrapper")},t.ptm("contentWrapper")),[a("div",v({class:t.cx("content")},t.ptm("content")),[L(t.$slots,"default")],16)],16)],16,Et),[[Ve,!c.d_collapsed]])]}),_:3},16)],16,Dt)}I.render=jt;var Kt=`
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
`,qt={root:function(e){var l=e.instance,o=e.props;return["p-textarea p-component",{"p-filled":l.$filled,"p-textarea-resizable ":o.autoResize,"p-textarea-sm p-inputfield-sm":o.size==="small","p-textarea-lg p-inputfield-lg":o.size==="large","p-invalid":l.$invalid,"p-variant-filled":l.$variant==="filled","p-textarea-fluid":l.$fluid}]}},Ft=H.extend({name:"textarea",style:Kt,classes:qt}),Ht={name:"BaseTextarea",extends:yt,props:{autoResize:Boolean},style:Ft,provide:function(){return{$pcTextarea:this,$parentInstance:this}}};function Q(t){"@babel/helpers - typeof";return Q=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},Q(t)}function Nt(t,e,l){return(e=Rt(e))in t?Object.defineProperty(t,e,{value:l,enumerable:!0,configurable:!0,writable:!0}):t[e]=l,t}function Rt(t){var e=Mt(t,"string");return Q(e)=="symbol"?e:e+""}function Mt(t,e){if(Q(t)!="object"||!t)return t;var l=t[Symbol.toPrimitive];if(l!==void 0){var o=l.call(t,e);if(Q(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var oe={name:"Textarea",extends:Ht,inheritAttrs:!1,observer:null,mounted:function(){var e=this;this.autoResize&&(this.observer=new ResizeObserver(function(){requestAnimationFrame(function(){e.resize()})}),this.observer.observe(this.$el))},updated:function(){this.autoResize&&this.resize()},beforeUnmount:function(){this.observer&&this.observer.disconnect()},methods:{resize:function(){if(this.$el.offsetParent){var e=this.$el.style.height,l=parseInt(e)||0,o=this.$el.scrollHeight,c=!l||o>l,i=l&&o<l;i?(this.$el.style.height="auto",this.$el.style.height="".concat(this.$el.scrollHeight,"px")):c&&(this.$el.style.height="".concat(o,"px"))}},onInput:function(e){this.autoResize&&this.resize(),this.writeValue(e.target.value,e)}},computed:{attrs:function(){return v(this.ptmi("root",{context:{filled:this.$filled,disabled:this.disabled}}),this.formField)},dataP:function(){return ie(Nt({invalid:this.$invalid,fluid:this.$fluid,filled:this.$variant==="filled"},this.size,this.size))}}},Wt=["value","name","disabled","aria-invalid","data-p"];function Zt(t,e,l,o,c,i){return b(),f("textarea",v({class:t.cx("root"),value:t.d_value,name:t.name,disabled:t.disabled,"aria-invalid":t.invalid||void 0,"data-p":i.dataP,onInput:e[0]||(e[0]=function(){return i.onInput&&i.onInput.apply(i,arguments)})},i.attrs),null,16,Wt)}oe.render=Zt;var Ne={name:"ChevronLeftIcon",extends:_e};function Gt(t){return Yt(t)||Xt(t)||Jt(t)||Qt()}function Qt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Jt(t,e){if(t){if(typeof t=="string")return ye(t,e);var l={}.toString.call(t).slice(8,-1);return l==="Object"&&t.constructor&&(l=t.constructor.name),l==="Map"||l==="Set"?Array.from(t):l==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(l)?ye(t,e):void 0}}function Xt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Yt(t){if(Array.isArray(t))return ye(t)}function ye(t,e){(e==null||e>t.length)&&(e=t.length);for(var l=0,o=Array(e);l<e;l++)o[l]=t[l];return o}function en(t,e,l,o,c,i){return b(),f("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Gt(e[0]||(e[0]=[a("path",{d:"M9.61296 13C9.50997 13.0005 9.40792 12.9804 9.3128 12.9409C9.21767 12.9014 9.13139 12.8433 9.05902 12.7701L3.83313 7.54416C3.68634 7.39718 3.60388 7.19795 3.60388 6.99022C3.60388 6.78249 3.68634 6.58325 3.83313 6.43628L9.05902 1.21039C9.20762 1.07192 9.40416 0.996539 9.60724 1.00012C9.81032 1.00371 10.0041 1.08597 10.1477 1.22959C10.2913 1.37322 10.3736 1.56698 10.3772 1.77005C10.3808 1.97313 10.3054 2.16968 10.1669 2.31827L5.49496 6.99022L10.1669 11.6622C10.3137 11.8091 10.3962 12.0084 10.3962 12.2161C10.3962 12.4238 10.3137 12.6231 10.1669 12.7701C10.0945 12.8433 10.0083 12.9014 9.91313 12.9409C9.81801 12.9804 9.71596 13.0005 9.61296 13Z",fill:"currentColor"},null,-1)])),16)}Ne.render=en;var Re={name:"ChevronRightIcon",extends:_e};function tn(t){return on(t)||an(t)||ln(t)||nn()}function nn(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function ln(t,e){if(t){if(typeof t=="string")return he(t,e);var l={}.toString.call(t).slice(8,-1);return l==="Object"&&t.constructor&&(l=t.constructor.name),l==="Map"||l==="Set"?Array.from(t):l==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(l)?he(t,e):void 0}}function an(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function on(t){if(Array.isArray(t))return he(t)}function he(t,e){(e==null||e>t.length)&&(e=t.length);for(var l=0,o=Array(e);l<e;l++)o[l]=t[l];return o}function rn(t,e,l,o,c,i){return b(),f("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),tn(e[0]||(e[0]=[a("path",{d:"M4.38708 13C4.28408 13.0005 4.18203 12.9804 4.08691 12.9409C3.99178 12.9014 3.9055 12.8433 3.83313 12.7701C3.68634 12.6231 3.60388 12.4238 3.60388 12.2161C3.60388 12.0084 3.68634 11.8091 3.83313 11.6622L8.50507 6.99022L3.83313 2.31827C3.69467 2.16968 3.61928 1.97313 3.62287 1.77005C3.62645 1.56698 3.70872 1.37322 3.85234 1.22959C3.99596 1.08597 4.18972 1.00371 4.3928 1.00012C4.59588 0.996539 4.79242 1.07192 4.94102 1.21039L10.1669 6.43628C10.3137 6.58325 10.3962 6.78249 10.3962 6.99022C10.3962 7.19795 10.3137 7.39718 10.1669 7.54416L4.94102 12.7701C4.86865 12.8433 4.78237 12.9014 4.68724 12.9409C4.59212 12.9804 4.49007 13.0005 4.38708 13Z",fill:"currentColor"},null,-1)])),16)}Re.render=rn;var sn=`
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
`,dn={root:function(e){var l=e.props;return["p-tabview p-component",{"p-tabview-scrollable":l.scrollable}]},navContainer:"p-tabview-tablist-container",prevButton:"p-tabview-prev-button",navContent:"p-tabview-tablist-scroll-container",nav:"p-tabview-tablist",tab:{header:function(e){var l=e.instance,o=e.tab,c=e.index;return["p-tabview-tablist-item",l.getTabProp(o,"headerClass"),{"p-tabview-tablist-item-active":l.d_activeIndex===c,"p-disabled":l.getTabProp(o,"disabled")}]},headerAction:"p-tabview-tab-header",headerTitle:"p-tabview-tab-title",content:function(e){var l=e.instance,o=e.tab;return["p-tabview-panel",l.getTabProp(o,"contentClass")]}},inkbar:"p-tabview-ink-bar",nextButton:"p-tabview-next-button",panelContainer:"p-tabview-panels"},un=H.extend({name:"tabview",style:sn,classes:dn}),cn={name:"BaseTabView",extends:Te,props:{activeIndex:{type:Number,default:0},lazy:{type:Boolean,default:!1},scrollable:{type:Boolean,default:!1},tabindex:{type:Number,default:0},selectOnFocus:{type:Boolean,default:!1},prevButtonProps:{type:null,default:null},nextButtonProps:{type:null,default:null},prevIcon:{type:String,default:void 0},nextIcon:{type:String,default:void 0}},style:un,provide:function(){return{$pcTabs:void 0,$pcTabView:this,$parentInstance:this}}},Me={name:"TabView",extends:cn,inheritAttrs:!1,emits:["update:activeIndex","tab-change","tab-click"],data:function(){return{d_activeIndex:this.activeIndex,isPrevButtonDisabled:!0,isNextButtonDisabled:!1}},watch:{activeIndex:function(e){this.d_activeIndex=e,this.scrollInView({index:e})}},mounted:function(){console.warn("Deprecated since v4. Use Tabs component instead."),this.updateInkBar(),this.scrollable&&this.updateButtonState()},updated:function(){this.updateInkBar(),this.scrollable&&this.updateButtonState()},methods:{isTabPanel:function(e){return e.type.name==="TabPanel"},isTabActive:function(e){return this.d_activeIndex===e},getTabProp:function(e,l){return e.props?e.props[l]:void 0},getKey:function(e,l){return this.getTabProp(e,"header")||l},getTabHeaderActionId:function(e){return"".concat(this.$id,"_").concat(e,"_header_action")},getTabContentId:function(e){return"".concat(this.$id,"_").concat(e,"_content")},getTabPT:function(e,l,o){var c=this.tabs.length,i={props:e.props,parent:{instance:this,props:this.$props,state:this.$data},context:{index:o,count:c,first:o===0,last:o===c-1,active:this.isTabActive(o)}};return v(this.ptm("tabpanel.".concat(l),{tabpanel:i}),this.ptm("tabpanel.".concat(l),i),this.ptmo(this.getTabProp(e,"pt"),l,i))},onScroll:function(e){this.scrollable&&this.updateButtonState(),e.preventDefault()},onPrevButtonClick:function(){var e=this.$refs.content,l=Z(e),o=e.scrollLeft-l;e.scrollLeft=o<=0?0:o},onNextButtonClick:function(){var e=this.$refs.content,l=Z(e)-this.getVisibleButtonWidths(),o=e.scrollLeft+l,c=e.scrollWidth-l;e.scrollLeft=o>=c?c:o},onTabClick:function(e,l,o){this.changeActiveIndex(e,l,o),this.$emit("tab-click",{originalEvent:e,index:o})},onTabKeyDown:function(e,l,o){switch(e.code){case"ArrowLeft":this.onTabArrowLeftKey(e);break;case"ArrowRight":this.onTabArrowRightKey(e);break;case"Home":this.onTabHomeKey(e);break;case"End":this.onTabEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":case"Space":this.onTabEnterKey(e,l,o);break}},onTabArrowRightKey:function(e){var l=this.findNextHeaderAction(e.target.parentElement);l?this.changeFocusedTab(e,l):this.onTabHomeKey(e),e.preventDefault()},onTabArrowLeftKey:function(e){var l=this.findPrevHeaderAction(e.target.parentElement);l?this.changeFocusedTab(e,l):this.onTabEndKey(e),e.preventDefault()},onTabHomeKey:function(e){var l=this.findFirstHeaderAction();this.changeFocusedTab(e,l),e.preventDefault()},onTabEndKey:function(e){var l=this.findLastHeaderAction();this.changeFocusedTab(e,l),e.preventDefault()},onPageDownKey:function(e){this.scrollInView({index:this.$refs.nav.children.length-2}),e.preventDefault()},onPageUpKey:function(e){this.scrollInView({index:0}),e.preventDefault()},onTabEnterKey:function(e,l,o){this.changeActiveIndex(e,l,o),e.preventDefault()},findNextHeaderAction:function(e){var l=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,o=l?e:e.nextElementSibling;return o?ne(o,"data-p-disabled")||ne(o,"data-pc-section")==="inkbar"?this.findNextHeaderAction(o):ze(o,'[data-pc-section="headeraction"]'):null},findPrevHeaderAction:function(e){var l=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,o=l?e:e.previousElementSibling;return o?ne(o,"data-p-disabled")||ne(o,"data-pc-section")==="inkbar"?this.findPrevHeaderAction(o):ze(o,'[data-pc-section="headeraction"]'):null},findFirstHeaderAction:function(){return this.findNextHeaderAction(this.$refs.nav.firstElementChild,!0)},findLastHeaderAction:function(){return this.findPrevHeaderAction(this.$refs.nav.lastElementChild,!0)},changeActiveIndex:function(e,l,o){!this.getTabProp(l,"disabled")&&this.d_activeIndex!==o&&(this.d_activeIndex=o,this.$emit("update:activeIndex",o),this.$emit("tab-change",{originalEvent:e,index:o}),this.scrollInView({index:o}))},changeFocusedTab:function(e,l){if(l&&(dt(l),this.scrollInView({element:l}),this.selectOnFocus)){var o=parseInt(l.parentElement.dataset.pcIndex,10),c=this.tabs[o];this.changeActiveIndex(e,c,o)}},scrollInView:function(e){var l=e.element,o=e.index,c=o===void 0?-1:o,i=l||this.$refs.nav.children[c];i&&i.scrollIntoView&&i.scrollIntoView({block:"nearest"})},updateInkBar:function(){var e=this.$refs.nav.children[this.d_activeIndex];this.$refs.inkbar.style.width=Z(e)+"px",this.$refs.inkbar.style.left=Ue(e).left-Ue(this.$refs.nav).left+"px"},updateButtonState:function(){var e=this.$refs.content,l=e.scrollLeft,o=e.scrollWidth,c=Z(e);this.isPrevButtonDisabled=l===0,this.isNextButtonDisabled=parseInt(l)===o-c},getVisibleButtonWidths:function(){var e=this.$refs,l=e.prevBtn,o=e.nextBtn;return[l,o].reduce(function(c,i){return i?c+Z(i):c},0)}},computed:{tabs:function(){var e=this;return this.$slots.default().reduce(function(l,o){return e.isTabPanel(o)?l.push(o):o.children&&o.children instanceof Array&&o.children.forEach(function(c){e.isTabPanel(c)&&l.push(c)}),l},[])},prevButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.previous:void 0},nextButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.next:void 0}},directives:{ripple:re},components:{ChevronLeftIcon:Ne,ChevronRightIcon:Re}};function J(t){"@babel/helpers - typeof";return J=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},J(t)}function qe(t,e){var l=Object.keys(t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);e&&(o=o.filter(function(c){return Object.getOwnPropertyDescriptor(t,c).enumerable})),l.push.apply(l,o)}return l}function C(t){for(var e=1;e<arguments.length;e++){var l=arguments[e]!=null?arguments[e]:{};e%2?qe(Object(l),!0).forEach(function(o){pn(t,o,l[o])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(l)):qe(Object(l)).forEach(function(o){Object.defineProperty(t,o,Object.getOwnPropertyDescriptor(l,o))})}return t}function pn(t,e,l){return(e=bn(e))in t?Object.defineProperty(t,e,{value:l,enumerable:!0,configurable:!0,writable:!0}):t[e]=l,t}function bn(t){var e=fn(t,"string");return J(e)=="symbol"?e:e+""}function fn(t,e){if(J(t)!="object"||!t)return t;var l=t[Symbol.toPrimitive];if(l!==void 0){var o=l.call(t,e);if(J(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var gn=["tabindex","aria-label"],vn=["data-p-active","data-p-disabled","data-pc-index"],mn=["id","tabindex","aria-disabled","aria-selected","aria-controls","onClick","onKeydown"],yn=["tabindex","aria-label"],hn=["id","aria-labelledby","data-pc-index","data-p-active"];function xn(t,e,l,o,c,i){var x=ke("ripple");return b(),f("div",v({class:t.cx("root"),role:"tablist"},t.ptmi("root")),[a("div",v({class:t.cx("navContainer")},t.ptm("navContainer")),[t.scrollable&&!c.isPrevButtonDisabled?z((b(),f("button",v({key:0,ref:"prevBtn",type:"button",class:t.cx("prevButton"),tabindex:t.tabindex,"aria-label":i.prevButtonAriaLabel,onClick:e[0]||(e[0]=function(){return i.onPrevButtonClick&&i.onPrevButtonClick.apply(i,arguments)})},C(C({},t.prevButtonProps),t.ptm("prevButton")),{"data-pc-group-section":"navbutton"}),[L(t.$slots,"previcon",{},function(){return[(b(),O(q(t.prevIcon?"span":"ChevronLeftIcon"),v({"aria-hidden":"true",class:t.prevIcon},t.ptm("prevIcon")),null,16,["class"]))]})],16,gn)),[[x]]):k("",!0),a("div",v({ref:"content",class:t.cx("navContent"),onScroll:e[1]||(e[1]=function(){return i.onScroll&&i.onScroll.apply(i,arguments)})},t.ptm("navContent")),[a("ul",v({ref:"nav",class:t.cx("nav")},t.ptm("nav")),[(b(!0),f(U,null,F(i.tabs,function(p,g){return b(),f("li",v({key:i.getKey(p,g),style:i.getTabProp(p,"headerStyle"),class:t.cx("tab.header",{tab:p,index:g}),role:"presentation"},{ref_for:!0},C(C(C({},i.getTabProp(p,"headerProps")),i.getTabPT(p,"root",g)),i.getTabPT(p,"header",g)),{"data-pc-name":"tabpanel","data-p-active":c.d_activeIndex===g,"data-p-disabled":i.getTabProp(p,"disabled"),"data-pc-index":g}),[z((b(),f("a",v({id:i.getTabHeaderActionId(g),class:t.cx("tab.headerAction"),tabindex:i.getTabProp(p,"disabled")||!i.isTabActive(g)?-1:t.tabindex,role:"tab","aria-disabled":i.getTabProp(p,"disabled"),"aria-selected":i.isTabActive(g),"aria-controls":i.getTabContentId(g),onClick:function(D){return i.onTabClick(D,p,g)},onKeydown:function(D){return i.onTabKeyDown(D,p,g)}},{ref_for:!0},C(C({},i.getTabProp(p,"headerActionProps")),i.getTabPT(p,"headerAction",g))),[p.props&&p.props.header?(b(),f("span",v({key:0,class:t.cx("tab.headerTitle")},{ref_for:!0},i.getTabPT(p,"headerTitle",g)),P(p.props.header),17)):k("",!0),p.children&&p.children.header?(b(),O(q(p.children.header),{key:1})):k("",!0)],16,mn)),[[x]])],16,vn)}),128)),a("li",v({ref:"inkbar",class:t.cx("inkbar"),role:"presentation","aria-hidden":"true"},t.ptm("inkbar")),null,16)],16)],16),t.scrollable&&!c.isNextButtonDisabled?z((b(),f("button",v({key:1,ref:"nextBtn",type:"button",class:t.cx("nextButton"),tabindex:t.tabindex,"aria-label":i.nextButtonAriaLabel,onClick:e[2]||(e[2]=function(){return i.onNextButtonClick&&i.onNextButtonClick.apply(i,arguments)})},C(C({},t.nextButtonProps),t.ptm("nextButton")),{"data-pc-group-section":"navbutton"}),[L(t.$slots,"nexticon",{},function(){return[(b(),O(q(t.nextIcon?"span":"ChevronRightIcon"),v({"aria-hidden":"true",class:t.nextIcon},t.ptm("nextIcon")),null,16,["class"]))]})],16,yn)),[[x]]):k("",!0)],16),a("div",v({class:t.cx("panelContainer")},t.ptm("panelContainer")),[(b(!0),f(U,null,F(i.tabs,function(p,g){return b(),f(U,{key:i.getKey(p,g)},[!t.lazy||i.isTabActive(g)?z((b(),f("div",v({key:0,id:i.getTabContentId(g),style:i.getTabProp(p,"contentStyle"),class:t.cx("tab.content",{tab:p}),role:"tabpanel","aria-labelledby":i.getTabHeaderActionId(g)},{ref_for:!0},C(C(C({},i.getTabProp(p,"contentProps")),i.getTabPT(p,"root",g)),i.getTabPT(p,"content",g)),{"data-pc-name":"tabpanel","data-pc-index":g,"data-p-active":c.d_activeIndex===g}),[(b(),O(q(p)))],16,hn)),[[Ve,t.lazy?!0:i.isTabActive(g)]]):k("",!0)],64)}),128))],16)],16)}Me.render=xn;var wn={root:function(e){var l=e.instance;return["p-tabpanel",{"p-tabpanel-active":l.active}]}},kn=H.extend({name:"tabpanel",classes:wn}),Vn={name:"BaseTabPanel",extends:Te,props:{value:{type:[String,Number],default:void 0},as:{type:[String,Object],default:"DIV"},asChild:{type:Boolean,default:!1},header:null,headerStyle:null,headerClass:null,headerProps:null,headerActionProps:null,contentStyle:null,contentClass:null,contentProps:null,disabled:Boolean},style:kn,provide:function(){return{$pcTabPanel:this,$parentInstance:this}}},E={name:"TabPanel",extends:Vn,inheritAttrs:!1,inject:["$pcTabs"],computed:{active:function(){var e;return ae((e=this.$pcTabs)===null||e===void 0?void 0:e.d_value,this.value)},id:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tabpanel_").concat(this.value)},ariaLabelledby:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tab_").concat(this.value)},attrs:function(){return v(this.a11yAttrs,this.ptmi("root",this.ptParams))},a11yAttrs:function(){var e;return{id:this.id,tabindex:(e=this.$pcTabs)===null||e===void 0?void 0:e.tabindex,role:"tabpanel","aria-labelledby":this.ariaLabelledby,"data-pc-name":"tabpanel","data-p-active":this.active}},ptParams:function(){return{context:{active:this.active}}}}};function _n(t,e,l,o,c,i){var x,p;return i.$pcTabs?(b(),f(U,{key:1},[t.asChild?L(t.$slots,"default",{key:1,class:j(t.cx("root")),active:i.active,a11yAttrs:i.a11yAttrs}):(b(),f(U,{key:0},[!((x=i.$pcTabs)!==null&&x!==void 0&&x.lazy)||i.active?z((b(),O(q(t.as),v({key:0,class:t.cx("root")},i.attrs),{default:y(function(){return[L(t.$slots,"default")]}),_:3},16,["class"])),[[Ve,(p=i.$pcTabs)!==null&&p!==void 0&&p.lazy?!0:i.active]]):k("",!0)],64))],64)):L(t.$slots,"default",{key:0})}E.render=_n;var Tn=`
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
`,Pn={root:function(e){var l=e.instance,o=e.props;return["p-togglebutton p-component",{"p-togglebutton-checked":l.active,"p-invalid":l.$invalid,"p-togglebutton-fluid":o.fluid,"p-togglebutton-sm p-inputfield-sm":o.size==="small","p-togglebutton-lg p-inputfield-lg":o.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},$n=H.extend({name:"togglebutton",style:Tn,classes:Pn}),Sn={name:"BaseToggleButton",extends:Fe,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:$n,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}};function X(t){"@babel/helpers - typeof";return X=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},X(t)}function An(t,e,l){return(e=Cn(e))in t?Object.defineProperty(t,e,{value:l,enumerable:!0,configurable:!0,writable:!0}):t[e]=l,t}function Cn(t){var e=In(t,"string");return X(e)=="symbol"?e:e+""}function In(t,e){if(X(t)!="object"||!t)return t;var l=t[Symbol.toPrimitive];if(l!==void 0){var o=l.call(t,e);if(X(o)!="object")return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var We={name:"ToggleButton",extends:Sn,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(e){var l=e==="root"?this.ptmi:this.ptm;return l(e,{context:{active:this.active,disabled:this.disabled}})},onChange:function(e){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,e),this.$emit("change",e))},onBlur:function(e){var l,o;(l=(o=this.formField).onBlur)===null||l===void 0||l.call(o,e)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return Oe(this.onLabel)&&Oe(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "},dataP:function(){return ie(An({checked:this.active,invalid:this.$invalid},this.size,this.size))}},directives:{ripple:re}},Bn=["tabindex","disabled","aria-pressed","aria-label","aria-labelledby","data-p-checked","data-p-disabled","data-p"],Ln=["data-p"];function Dn(t,e,l,o,c,i){var x=ke("ripple");return z((b(),f("button",v({type:"button",class:t.cx("root"),tabindex:t.tabindex,disabled:t.disabled,"aria-pressed":t.d_value,onClick:e[0]||(e[0]=function(){return i.onChange&&i.onChange.apply(i,arguments)}),onBlur:e[1]||(e[1]=function(){return i.onBlur&&i.onBlur.apply(i,arguments)})},i.getPTOptions("root"),{"aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"data-p-checked":i.active,"data-p-disabled":t.disabled,"data-p":i.dataP}),[a("span",v({class:t.cx("content")},i.getPTOptions("content"),{"data-p":i.dataP}),[L(t.$slots,"default",{},function(){return[L(t.$slots,"icon",{value:t.d_value,class:j(t.cx("icon"))},function(){return[t.onIcon||t.offIcon?(b(),f("span",v({key:0,class:[t.cx("icon"),t.d_value?t.onIcon:t.offIcon]},i.getPTOptions("icon")),null,16)):k("",!0)]}),a("span",v({class:t.cx("label")},i.getPTOptions("label")),P(i.label),17)]})],16,Ln)],16,Bn)),[[x]])}We.render=Dn;var Un=`
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
`,zn={root:function(e){var l=e.props,o=e.instance;return["p-selectbutton p-component",{"p-invalid":o.$invalid,"p-selectbutton-fluid":l.fluid}]}},On=H.extend({name:"selectbutton",style:Un,classes:zn}),En={name:"BaseSelectButton",extends:Fe,props:{options:Array,optionLabel:null,optionValue:null,optionDisabled:null,multiple:Boolean,allowEmpty:{type:Boolean,default:!0},dataKey:null,ariaLabelledby:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:On,provide:function(){return{$pcSelectButton:this,$parentInstance:this}}};function jn(t,e){var l=typeof Symbol<"u"&&t[Symbol.iterator]||t["@@iterator"];if(!l){if(Array.isArray(t)||(l=Ze(t))||e){l&&(t=l);var o=0,c=function(){};return{s:c,n:function(){return o>=t.length?{done:!0}:{done:!1,value:t[o++]}},e:function($){throw $},f:c}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var i,x=!0,p=!1;return{s:function(){l=l.call(t)},n:function(){var $=l.next();return x=$.done,$},e:function($){p=!0,i=$},f:function(){try{x||l.return==null||l.return()}finally{if(p)throw i}}}}function Kn(t){return Hn(t)||Fn(t)||Ze(t)||qn()}function qn(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Ze(t,e){if(t){if(typeof t=="string")return xe(t,e);var l={}.toString.call(t).slice(8,-1);return l==="Object"&&t.constructor&&(l=t.constructor.name),l==="Map"||l==="Set"?Array.from(t):l==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(l)?xe(t,e):void 0}}function Fn(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Hn(t){if(Array.isArray(t))return xe(t)}function xe(t,e){(e==null||e>t.length)&&(e=t.length);for(var l=0,o=Array(e);l<e;l++)o[l]=t[l];return o}var we={name:"SelectButton",extends:En,inheritAttrs:!1,emits:["change"],methods:{getOptionLabel:function(e){return this.optionLabel?le(e,this.optionLabel):e},getOptionValue:function(e){return this.optionValue?le(e,this.optionValue):e},getOptionRenderKey:function(e){return this.dataKey?le(e,this.dataKey):this.getOptionLabel(e)},isOptionDisabled:function(e){return this.optionDisabled?le(e,this.optionDisabled):!1},isOptionReadonly:function(e){if(this.allowEmpty)return!1;var l=this.isSelected(e);return this.multiple?l&&this.d_value.length===1:l},onOptionSelect:function(e,l,o){var c=this;if(!(this.disabled||this.isOptionDisabled(l)||this.isOptionReadonly(l))){var i=this.isSelected(l),x=this.getOptionValue(l),p;if(this.multiple)if(i){if(p=this.d_value.filter(function(g){return!ae(g,x,c.equalityKey)}),!this.allowEmpty&&p.length===0)return}else p=this.d_value?[].concat(Kn(this.d_value),[x]):[x];else{if(i&&!this.allowEmpty)return;p=i?null:x}this.writeValue(p,e),this.$emit("change",{originalEvent:e,value:p})}},isSelected:function(e){var l=!1,o=this.getOptionValue(e);if(this.multiple){if(this.d_value){var c=jn(this.d_value),i;try{for(c.s();!(i=c.n()).done;){var x=i.value;if(ae(x,o,this.equalityKey)){l=!0;break}}}catch(p){c.e(p)}finally{c.f()}}}else l=ae(this.d_value,o,this.equalityKey);return l}},computed:{equalityKey:function(){return this.optionValue?null:this.dataKey},dataP:function(){return ie({invalid:this.$invalid})}},directives:{ripple:re},components:{ToggleButton:We}},Nn=["aria-labelledby","data-p"];function Rn(t,e,l,o,c,i){var x=ut("ToggleButton");return b(),f("div",v({class:t.cx("root"),role:"group","aria-labelledby":t.ariaLabelledby},t.ptmi("root"),{"data-p":i.dataP}),[(b(!0),f(U,null,F(t.options,function(p,g){return b(),O(x,{key:i.getOptionRenderKey(p),modelValue:i.isSelected(p),onLabel:i.getOptionLabel(p),offLabel:i.getOptionLabel(p),disabled:t.disabled||i.isOptionDisabled(p),unstyled:t.unstyled,size:t.size,readonly:i.isOptionReadonly(p),onChange:function(D){return i.onOptionSelect(D,p,g)},pt:t.ptm("pcToggleButton")},ct({_:2},[t.$slots.option?{name:"default",fn:y(function(){return[L(t.$slots,"option",{option:p,index:g},function(){return[a("span",v({ref_for:!0},t.ptm("pcToggleButton").label),P(i.getOptionLabel(p)),17)]})]}),key:"0"}:void 0]),1032,["modelValue","onLabel","offLabel","disabled","unstyled","size","readonly","onChange","pt"])}),128))],16,Nn)}we.render=Rn;const Mn={class:"p-4 flex flex-col gap-4"},Wn={key:0,class:"flex justify-center"},Zn={key:1},Gn={class:"flex flex-col gap-6"},Qn={class:"flex flex-col gap-4"},Jn={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},Xn={class:"flex flex-col gap-2"},Yn={class:"flex flex-col gap-2"},el={class:"flex flex-col gap-2"},tl={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},nl={class:"flex items-center gap-2"},ll=["for"],al={class:"flex flex-col gap-2"},ol={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},rl=["for"],il={class:"flex flex-col gap-4"},sl={class:"flex flex-col gap-2"},dl={class:"flex flex-col gap-4"},ul={class:"flex items-center gap-2 p-3 bg-gray-800 rounded border border-gray-700"},cl={key:0,class:"flex flex-col gap-2"},pl={class:"flex items-center gap-2"},bl={key:0,class:"flex flex-col gap-6 mt-4"},fl={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},gl={class:"flex flex-col gap-2"},vl={class:"flex flex-col gap-2"},ml={class:"flex flex-col gap-2"},yl={class:"flex flex-col gap-2"},hl={class:"grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 pt-4"},xl={class:"flex flex-col gap-2"},wl={class:"flex flex-col gap-2"},kl={class:"flex flex-col gap-3 border border-green-600/50 rounded bg-green-900/10 p-4"},Vl={class:"flex items-center gap-2"},_l={key:0,class:"ml-8"},Tl={key:1,class:"text-gray-400 italic"},Pl={class:"flex flex-col gap-6"},$l={class:"flex items-center gap-2"},Sl={key:0,class:"flex flex-col gap-4"},Al={class:"flex flex-col gap-2"},Cl={class:"flex flex-col gap-2"},Il={class:"flex items-center gap-2"},Bl={key:0,class:"flex flex-col gap-4"},Ll={class:"flex flex-col gap-2"},Dl={class:"flex flex-col gap-2"},Ul={class:"flex items-center gap-2"},zl={key:0,class:"flex flex-col gap-4"},Ol={class:"flex flex-col gap-2"},El={class:"flex items-center gap-2"},jl={key:0,class:"flex flex-col gap-4"},Kl={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},ql={class:"flex flex-col gap-2"},Fl={class:"flex flex-col gap-2"},Hl={class:"flex flex-col gap-2"},Nl={class:"flex flex-col gap-2"},Rl={class:"flex flex-col gap-2"},Ml={class:"flex flex-col gap-2"},Wl={class:"flex flex-col gap-6"},Zl={class:"flex items-center gap-2"},Gl={key:0,class:"flex flex-col gap-6"},Ql={class:"bg-gray-800 p-4 rounded border border-gray-700 mt-4"},Jl={key:0,class:"grid grid-cols-1 md:grid-cols-2 gap-4 text-sm"},Xl={class:"flex justify-between border-b border-gray-700 py-2"},Yl={class:"font-mono"},ea={class:"flex justify-between border-b border-gray-700 py-2"},ta={class:"flex justify-between border-b border-gray-700 py-2"},na={class:"font-mono text-lg"},la={class:"flex justify-between border-b border-gray-700 py-2"},aa={class:"flex justify-between border-b border-gray-700 py-2"},oa={class:"font-mono"},ra={key:1,class:"text-center py-4 text-gray-500"},ia={class:"flex flex-col gap-6"},sa={class:"flex flex-col gap-4"},da={class:"flex flex-col gap-2"},ua={class:"flex items-center gap-2 mt-2"},ca={class:"flex items-center gap-2"},pa={key:0,class:"flex flex-col gap-4"},ba={class:"bg-yellow-900/20 border border-yellow-600/50 p-3 rounded text-yellow-200 text-sm flex items-start gap-2"},fa={class:"grid grid-cols-1 md:grid-cols-2 gap-6"},ga={class:"flex flex-col gap-2"},va={class:"flex flex-col gap-2"},ma={class:"grid grid-cols-1 xl:grid-cols-2 gap-6"},ya={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},ha={class:"flex items-center justify-between bg-gray-900/50 p-3 rounded"},xa={class:"font-mono"},wa={class:"text-right"},ka={class:"font-mono text-green-400"},Va={key:0,class:"bg-blue-900/20 border border-blue-600/50 p-3 rounded mt-2 flex flex-col gap-2"},_a={class:"flex flex-col gap-2 mt-2 border-t border-gray-700 pt-2"},Ta={class:"flex gap-2"},Pa={class:"flex justify-between items-center mt-1"},$a={class:"flex items-center gap-2"},Sa={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},Aa={class:"flex flex-col gap-2 mb-2"},Ca={class:"flex items-center justify-between"},Ia={class:"flex items-center gap-2"},Ba={key:0,class:"grid grid-cols-2 gap-2 text-sm bg-gray-900/30 p-2 rounded"},La={class:"flex flex-col"},Da={class:"flex flex-col"},Ua={class:"col-span-2 flex items-center gap-2 mt-1"},za={class:"flex gap-2"},Oa={class:"mt-2 max-h-40 overflow-y-auto"},Ea={class:"truncate"},ja={class:"flex gap-1"},Ka={class:"border-t border-gray-700 pt-3 mt-2"},qa={class:"flex items-center gap-2 mb-2"},Fa={key:0,class:"flex flex-col gap-2"},Ha={class:"flex flex-col gap-1"},Na={class:"flex flex-col gap-1"},Ra={class:"flex flex-col gap-1"},Ma={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3 xl:col-span-2"},Wa={class:"flex gap-4"},Za={class:"flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4 sticky bottom-0 bg-gray-900/90 backdrop-blur p-4 z-10"},Ga={class:"flex flex-col gap-4"},Qa={class:"flex flex-col gap-2"},Ja={class:"flex flex-col gap-2"},Xa={key:0,class:"text-red-500"},Ya={class:"flex flex-col gap-4"},co={__name:"Config",setup(t){const e=h({idm:{host:"",port:502,circuits:["A"],zones:[]},metrics:{url:""},web:{write_enabled:!1},logging:{interval:60,realtime_mode:!1},mqtt:{enabled:!1,broker:"",port:1883,username:"",topic_prefix:"idm/heatpump",qos:0,use_tls:!1,publish_interval:60,ha_discovery_enabled:!1,ha_discovery_prefix:"homeassistant"},network_security:{enabled:!1,whitelist:[],blacklist:[]},signal:{enabled:!1,cli_path:"signal-cli",sender:"",recipients:[]},telegram:{enabled:!1,bot_token:"",chat_ids:[]},discord:{enabled:!1,webhook_url:""},email:{enabled:!1,smtp_server:"",smtp_port:587,username:"",sender:"",recipients:[]},webdav:{enabled:!1,url:"",username:""},ai:{enabled:!1,sensitivity:3,model:"rolling"},updates:{enabled:!1,interval_hours:12,mode:"apply",target:"all",channel:"dev"},backup:{enabled:!1,interval:24,retention:10,auto_upload:!1}});h([{label:"Statistisch (Rolling Window)",value:"rolling"},{label:"Isolation Forest (Expert)",value:"isolation_forest"}]);const l=h(!1),o=h(""),c=h(""),i=h(""),x=h(""),p=h(""),g=h(""),$=h(""),D=h(""),Y=h(""),ee=h(""),N=h({}),Ge=h({}),B=h(null),Pe=h(!1),se=h(!1),$e=h(""),Se=h(!0),de=h(!1),m=pt(),te=bt();let ue=null;const ce=ft(()=>o.value&&c.value&&o.value!==c.value);gt(()=>{ue&&clearInterval(ue)});const Ae=h([]),Ce=h(!1),pe=h(!1),Ie=h(!1),R=h(null),be=h(null),M=h(!1),W=h(""),fe=h(!1),ge=h(!1);vt(async()=>{try{const u=await V.get("/api/config");e.value=u.data,e.value.network_security&&(g.value=(e.value.network_security.whitelist||[]).join(`
`),$.value=(e.value.network_security.blacklist||[]).join(`
`)),e.value.signal&&(D.value=(e.value.signal.recipients||[]).join(`
`)),e.value.telegram&&(Y.value=(e.value.telegram.chat_ids||[]).join(", ")),e.value.email&&(ee.value=(e.value.email.recipients||[]).join(", "));try{const n=await V.get("/api/health");$e.value=n.data.client_ip||"Unbekannt"}catch(n){console.error("Failed to get client IP",n)}ve(),Be(),Le(),ue=setInterval(Le,1e4)}catch{m.add({severity:"error",summary:"Fehler",detail:"Konfiguration konnte nicht geladen werden",life:3e3})}finally{Se.value=!1}});const Qe=async()=>{try{const u=await V.post("/api/signal/test",{message:"Signal Test vom IDM Metrics Collector"});u.data.success?m.add({severity:"success",summary:"Erfolg",detail:u.data.message,life:3e3}):m.add({severity:"error",summary:"Fehler",detail:u.data.error||"Signal Test fehlgeschlagen",life:3e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||u.message,life:5e3})}},Be=async()=>{Pe.value=!0;try{const[u,n]=await Promise.all([V.get("/api/check-update",{params:{channel:e.value.updates?.channel||"dev"}}),V.get("/api/signal/status")]);N.value=u.data,Ge.value=n.data}catch(u){console.error("Status load failed",u)}finally{Pe.value=!1}},Je=async()=>{se.value=!0;try{const u=await V.get("/api/check-update",{params:{channel:e.value.updates.channel}});N.value=u.data,u.data.update_available?m.add({severity:"info",summary:"Update verfügbar",detail:`Version ${u.data.latest_version} ist verfügbar.`,life:5e3}):m.add({severity:"success",summary:"System aktuell",detail:"Keine Updates gefunden.",life:3e3})}catch{m.add({severity:"error",summary:"Fehler",detail:"Update-Prüfung fehlgeschlagen",life:3e3})}finally{se.value=!1}},Xe=()=>{l.value=!1,De()},Le=async()=>{try{const u=await V.get("/api/ai/status");B.value=u.data}catch(u){console.error("Failed to load AI status",u)}},De=async()=>{de.value=!0;try{const u={idm_host:e.value.idm.host,idm_port:e.value.idm.port,circuits:e.value.idm.circuits,zones:e.value.idm.zones,metrics_url:e.value.metrics.url,write_enabled:e.value.web.write_enabled,logging_interval:e.value.logging.interval,realtime_mode:e.value.logging.realtime_mode,mqtt_enabled:e.value.mqtt?.enabled||!1,mqtt_broker:e.value.mqtt?.broker||"",mqtt_port:e.value.mqtt?.port||1883,mqtt_username:e.value.mqtt?.username||"",mqtt_password:i.value||void 0,mqtt_topic_prefix:e.value.mqtt?.topic_prefix||"idm/heatpump",mqtt_qos:e.value.mqtt?.qos||0,mqtt_use_tls:e.value.mqtt?.use_tls||!1,mqtt_publish_interval:e.value.mqtt?.publish_interval||60,mqtt_ha_discovery_enabled:e.value.mqtt?.ha_discovery_enabled||!1,mqtt_ha_discovery_prefix:e.value.mqtt?.ha_discovery_prefix||"homeassistant",network_security_enabled:e.value.network_security?.enabled||!1,network_security_whitelist:g.value,network_security_blacklist:$.value,signal_enabled:e.value.signal?.enabled||!1,signal_sender:e.value.signal?.sender||"",signal_cli_path:e.value.signal?.cli_path||"signal-cli",signal_recipients:D.value,telegram_enabled:e.value.telegram?.enabled||!1,telegram_bot_token:e.value.telegram?.bot_token||"",telegram_chat_ids:Y.value,discord_enabled:e.value.discord?.enabled||!1,discord_webhook_url:e.value.discord?.webhook_url||"",email_enabled:e.value.email?.enabled||!1,email_smtp_server:e.value.email?.smtp_server||"",email_smtp_port:e.value.email?.smtp_port||587,email_username:e.value.email?.username||"",email_password:x.value||void 0,email_sender:e.value.email?.sender||"",email_recipients:ee.value,webdav_enabled:e.value.webdav?.enabled||!1,webdav_url:e.value.webdav?.url||"",webdav_username:e.value.webdav?.username||"",webdav_password:p.value||void 0,ai_enabled:e.value.ai?.enabled||!1,ai_sensitivity:e.value.ai?.sensitivity||3,ai_model:e.value.ai?.model||"rolling",updates_enabled:e.value.updates?.enabled||!1,updates_interval_hours:e.value.updates?.interval_hours||12,updates_mode:e.value.updates?.mode||"apply",updates_target:e.value.updates?.target||"all",updates_channel:e.value.updates?.channel||"dev",backup_enabled:e.value.backup?.enabled||!1,backup_interval:e.value.backup?.interval||24,backup_retention:e.value.backup?.retention||10,backup_auto_upload:e.value.backup?.auto_upload||!1,new_password:o.value||void 0},n=await V.post("/api/config",u);m.add({severity:"success",summary:"Erfolg",detail:n.data.message||"Einstellungen erfolgreich gespeichert",life:3e3}),o.value="",c.value="",i.value="",p.value=""}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||u.message,life:5e3})}finally{de.value=!1}},Ye=()=>{te.require({message:"Bist du sicher, dass du den Dienst neu starten möchtest?",header:"Bestätigung",icon:"pi pi-exclamation-triangle",accept:async()=>{try{const u=await V.post("/api/restart");m.add({severity:"info",summary:"Neustart",detail:u.data.message,life:3e3})}catch{m.add({severity:"error",summary:"Fehler",detail:"Neustart fehlgeschlagen",life:3e3})}}})},ve=async()=>{Ce.value=!0;try{const u=await V.get("/api/backup/list");Ae.value=u.data.backups||[]}catch{m.add({severity:"error",summary:"Fehler",detail:"Backups konnten nicht geladen werden",life:3e3})}finally{Ce.value=!1}},et=async()=>{pe.value=!0;try{const u=await V.post("/api/backup/create");u.data.success?(m.add({severity:"success",summary:"Erfolg",detail:`Backup erstellt: ${u.data.filename}`,life:3e3}),ve()):m.add({severity:"error",summary:"Fehler",detail:u.data.error,life:3e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Backup Erstellung fehlgeschlagen",life:3e3})}finally{pe.value=!1}},tt=async u=>{try{const n=await V.get(`/api/backup/download/${u}`,{responseType:"blob"}),r=window.URL.createObjectURL(new Blob([n.data])),A=document.createElement("a");A.href=r,A.setAttribute("download",u),document.body.appendChild(A),A.click(),A.remove(),m.add({severity:"success",summary:"Erfolg",detail:"Backup heruntergeladen",life:2e3})}catch{m.add({severity:"error",summary:"Fehler",detail:"Backup Download fehlgeschlagen",life:3e3})}},nt=async u=>{try{m.add({severity:"info",summary:"Info",detail:"Upload gestartet...",life:2e3});const n=await V.post(`/api/backup/upload/${u}`);n.data.success?m.add({severity:"success",summary:"Erfolg",detail:"Backup erfolgreich hochgeladen",life:3e3}):m.add({severity:"error",summary:"Fehler",detail:n.data.error,life:5e3})}catch(n){m.add({severity:"error",summary:"Fehler",detail:n.response?.data?.error||"Upload fehlgeschlagen",life:5e3})}},lt=u=>{te.require({message:`Backup "${u}" löschen?`,header:"Backup Löschen",icon:"pi pi-trash",acceptClass:"p-button-danger",accept:async()=>{try{await V.delete(`/api/backup/delete/${u}`),m.add({severity:"success",summary:"Erfolg",detail:"Backup gelöscht",life:2e3}),ve()}catch{m.add({severity:"error",summary:"Fehler",detail:"Backup löschen fehlgeschlagen",life:3e3})}}})},at=u=>{const n=u.target.files[0];R.value=n},ot=async()=>{R.value&&te.require({message:"Konfiguration aus hochgeladener Datei wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!",header:"Aus Datei Wiederherstellen",icon:"pi pi-exclamation-triangle",acceptClass:"p-button-warning",accept:async()=>{Ie.value=!0;try{const u=new FormData;u.append("file",R.value),u.append("restore_secrets","false");const n=await V.post("/api/backup/restore",u,{headers:{"Content-Type":"multipart/form-data"}});n.data.success?(m.add({severity:"success",summary:"Erfolg",detail:n.data.message,life:5e3}),R.value=null,be.value&&(be.value.value=""),setTimeout(()=>location.reload(),2e3)):m.add({severity:"error",summary:"Fehler",detail:n.data.error,life:5e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Wiederherstellung fehlgeschlagen",life:5e3})}finally{Ie.value=!1}}})},rt=async()=>{if(W.value==="DELETE"){fe.value=!0;try{const u=await V.post("/api/database/delete");u.data.success?(m.add({severity:"success",summary:"Erfolg",detail:u.data.message,life:5e3}),M.value=!1,W.value=""):m.add({severity:"error",summary:"Fehler",detail:u.data.error,life:5e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Datenbank löschen fehlgeschlagen",life:5e3})}finally{fe.value=!1}}},it=()=>{te.require({message:"Update wirklich durchführen? Der Dienst wird neu gestartet.",header:"Update Bestätigung",icon:"pi pi-refresh",acceptClass:"p-button-info",accept:async()=>{ge.value=!0;try{const u=await V.post("/api/perform-update");u.data.success?(m.add({severity:"success",summary:"Update gestartet",detail:"System wird aktualisiert...",life:5e3}),setTimeout(Be,15e3)):m.add({severity:"error",summary:"Fehler",detail:u.data.error,life:5e3})}catch(u){m.add({severity:"error",summary:"Fehler",detail:u.response?.data?.error||"Update fehlgeschlagen",life:5e3})}finally{ge.value=!1}}})};return(u,n)=>(b(),f("div",Mn,[n[128]||(n[128]=a("h1",{class:"text-2xl font-bold mb-4"},"Konfiguration",-1)),Se.value?(b(),f("div",Wn,[...n[57]||(n[57]=[a("i",{class:"pi pi-spin pi-spinner text-4xl"},null,-1)])])):(b(),f("div",Zn,[d(s(Me),null,{default:y(()=>[d(s(E),{header:"Verbindung"},{default:y(()=>[a("div",Gn,[d(s(I),{legend:"IDM Wärmepumpe",toggleable:!0},{default:y(()=>[a("div",Qn,[a("div",Jn,[a("div",Xn,[n[58]||(n[58]=a("label",null,"Host / IP",-1)),d(s(w),{modelValue:e.value.idm.host,"onUpdate:modelValue":n[0]||(n[0]=r=>e.value.idm.host=r),class:"w-full"},null,8,["modelValue"])]),a("div",Yn,[n[59]||(n[59]=a("label",null,"Port",-1)),d(s(K),{modelValue:e.value.idm.port,"onUpdate:modelValue":n[1]||(n[1]=r=>e.value.idm.port=r),useGrouping:!1,class:"w-full"},null,8,["modelValue"])])]),a("div",el,[n[61]||(n[61]=a("label",{class:"font-bold"},"Aktivierte Heizkreise",-1)),a("div",tl,[a("div",nl,[d(s(_),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":n[2]||(n[2]=r=>e.value.idm.circuits=r),inputId:"circuitA",value:"A",disabled:""},null,8,["modelValue"]),n[60]||(n[60]=a("label",{for:"circuitA",class:"opacity-50"},"Heizkreis A (Fest)",-1))]),(b(),f(U,null,F(["B","C","D","E","F","G"],r=>a("div",{key:r,class:"flex items-center gap-2"},[d(s(_),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":n[3]||(n[3]=A=>e.value.idm.circuits=A),inputId:"circuit"+r,value:r},null,8,["modelValue","inputId","value"]),a("label",{for:"circuit"+r},"Heizkreis "+P(r),9,ll)])),64))])]),a("div",al,[n[62]||(n[62]=a("label",{class:"font-bold"},"Zonenmodule",-1)),a("div",ol,[(b(),f(U,null,F(10,r=>a("div",{key:r,class:"flex items-center gap-2"},[d(s(_),{modelValue:e.value.idm.zones,"onUpdate:modelValue":n[4]||(n[4]=A=>e.value.idm.zones=A),inputId:"zone"+(r-1),value:r-1},null,8,["modelValue","inputId","value"]),a("label",{for:"zone"+(r-1)},"Zone "+P(r),9,rl)])),64))])])])]),_:1}),d(s(I),{legend:"Datenbank (VictoriaMetrics)",toggleable:!0},{default:y(()=>[a("div",il,[a("div",sl,[n[63]||(n[63]=a("label",null,"Write URL",-1)),d(s(w),{modelValue:e.value.metrics.url,"onUpdate:modelValue":n[5]||(n[5]=r=>e.value.metrics.url=r),class:"w-full"},null,8,["modelValue"]),n[64]||(n[64]=a("small",{class:"text-gray-300"},"Standard: http://victoriametrics:8428/write",-1))])])]),_:1}),d(s(I),{legend:"Datenerfassung",toggleable:!0},{default:y(()=>[a("div",dl,[a("div",ul,[d(s(_),{modelValue:e.value.logging.realtime_mode,"onUpdate:modelValue":n[6]||(n[6]=r=>e.value.logging.realtime_mode=r),binary:"",inputId:"realtime_mode"},null,8,["modelValue"]),n[65]||(n[65]=a("div",{class:"flex flex-col"},[a("label",{for:"realtime_mode",class:"font-bold cursor-pointer"},"Echtzeit-Modus"),a("span",{class:"text-sm text-gray-400"},"Aktualisierung im Sekundentakt (Hohe Last)")],-1))]),e.value.logging.realtime_mode?k("",!0):(b(),f("div",cl,[n[66]||(n[66]=a("label",null,"Abfrage-Intervall (Sekunden)",-1)),d(s(K),{modelValue:e.value.logging.interval,"onUpdate:modelValue":n[7]||(n[7]=r=>e.value.logging.interval=r),min:1,max:3600,useGrouping:!1,class:"w-full md:w-1/2"},null,8,["modelValue"]),n[67]||(n[67]=a("small",{class:"text-gray-400"},"Standard: 60 Sekunden",-1))]))])]),_:1})])]),_:1}),d(s(E),{header:"MQTT & Integration"},{default:y(()=>[d(s(I),{legend:"MQTT Publishing",toggleable:!1},{legend:y(()=>[a("div",pl,[d(s(_),{modelValue:e.value.mqtt.enabled,"onUpdate:modelValue":n[8]||(n[8]=r=>e.value.mqtt.enabled=r),binary:"",inputId:"mqtt_enabled"},null,8,["modelValue"]),n[68]||(n[68]=a("span",{class:"font-bold text-lg"},"MQTT Aktivieren",-1))])]),default:y(()=>[e.value.mqtt.enabled?(b(),f("div",bl,[a("div",fl,[a("div",gl,[n[69]||(n[69]=a("label",null,"Broker Adresse",-1)),d(s(w),{modelValue:e.value.mqtt.broker,"onUpdate:modelValue":n[9]||(n[9]=r=>e.value.mqtt.broker=r),placeholder:"mqtt.example.com",class:"w-full"},null,8,["modelValue"])]),a("div",vl,[n[70]||(n[70]=a("label",null,"Port",-1)),d(s(K),{modelValue:e.value.mqtt.port,"onUpdate:modelValue":n[10]||(n[10]=r=>e.value.mqtt.port=r),useGrouping:!1,min:1,max:65535,class:"w-full"},null,8,["modelValue"])]),a("div",ml,[n[71]||(n[71]=a("label",null,"Benutzername",-1)),d(s(w),{modelValue:e.value.mqtt.username,"onUpdate:modelValue":n[11]||(n[11]=r=>e.value.mqtt.username=r),placeholder:"Optional",class:"w-full"},null,8,["modelValue"])]),a("div",yl,[n[72]||(n[72]=a("label",null,"Passwort",-1)),d(s(w),{modelValue:i.value,"onUpdate:modelValue":n[12]||(n[12]=r=>i.value=r),type:"password",placeholder:"••••••",class:"w-full"},null,8,["modelValue"])])]),a("div",hl,[a("div",xl,[n[73]||(n[73]=a("label",null,"Topic Präfix",-1)),d(s(w),{modelValue:e.value.mqtt.topic_prefix,"onUpdate:modelValue":n[13]||(n[13]=r=>e.value.mqtt.topic_prefix=r),class:"w-full"},null,8,["modelValue"])]),a("div",wl,[n[74]||(n[74]=a("label",null,"QoS Level",-1)),d(s(we),{modelValue:e.value.mqtt.qos,"onUpdate:modelValue":n[14]||(n[14]=r=>e.value.mqtt.qos=r),options:[0,1,2],"aria-labelledby":"basic",class:"w-full"},null,8,["modelValue"])])]),a("div",kl,[a("div",Vl,[d(s(_),{modelValue:e.value.mqtt.ha_discovery_enabled,"onUpdate:modelValue":n[15]||(n[15]=r=>e.value.mqtt.ha_discovery_enabled=r),binary:"",inputId:"ha_discovery"},null,8,["modelValue"]),n[75]||(n[75]=a("label",{for:"ha_discovery",class:"font-bold text-green-400 cursor-pointer"},"Home Assistant Auto-Discovery",-1))]),e.value.mqtt.ha_discovery_enabled?(b(),f("div",_l,[n[76]||(n[76]=a("label",{class:"text-sm"},"Discovery Präfix",-1)),d(s(w),{modelValue:e.value.mqtt.ha_discovery_prefix,"onUpdate:modelValue":n[16]||(n[16]=r=>e.value.mqtt.ha_discovery_prefix=r),class:"w-full mt-1"},null,8,["modelValue"])])):k("",!0)])])):(b(),f("div",Tl," Aktivieren Sie MQTT, um Daten an Broker wie Mosquitto oder Home Assistant zu senden. "))]),_:1})]),_:1}),d(s(E),{header:"Benachrichtigungen"},{default:y(()=>[a("div",Pl,[d(s(I),{legend:"Signal Messenger",toggleable:!0},{legend:y(()=>[a("div",$l,[d(s(_),{modelValue:e.value.signal.enabled,"onUpdate:modelValue":n[17]||(n[17]=r=>e.value.signal.enabled=r),binary:""},null,8,["modelValue"]),n[77]||(n[77]=a("span",{class:"font-bold"},"Signal",-1))])]),default:y(()=>[e.value.signal.enabled?(b(),f("div",Sl,[a("div",Al,[n[78]||(n[78]=a("label",null,"Sender Nummer",-1)),d(s(w),{modelValue:e.value.signal.sender,"onUpdate:modelValue":n[18]||(n[18]=r=>e.value.signal.sender=r),placeholder:"+49...",class:"w-full md:w-1/2"},null,8,["modelValue"])]),a("div",Cl,[n[79]||(n[79]=a("label",null,"Empfänger (Pro Zeile eine Nummer)",-1)),d(s(oe),{modelValue:D.value,"onUpdate:modelValue":n[19]||(n[19]=r=>D.value=r),rows:"3",class:"w-full font-mono"},null,8,["modelValue"])]),d(s(T),{label:"Testnachricht senden",icon:"pi pi-send",severity:"success",outlined:"",onClick:Qe,class:"w-full md:w-auto self-start"})])):k("",!0)]),_:1}),d(s(I),{legend:"Telegram",toggleable:!0},{legend:y(()=>[a("div",Il,[d(s(_),{modelValue:e.value.telegram.enabled,"onUpdate:modelValue":n[20]||(n[20]=r=>e.value.telegram.enabled=r),binary:""},null,8,["modelValue"]),n[80]||(n[80]=a("span",{class:"font-bold"},"Telegram",-1))])]),default:y(()=>[e.value.telegram.enabled?(b(),f("div",Bl,[a("div",Ll,[n[81]||(n[81]=a("label",null,"Bot Token",-1)),d(s(w),{modelValue:e.value.telegram.bot_token,"onUpdate:modelValue":n[21]||(n[21]=r=>e.value.telegram.bot_token=r),type:"password",class:"w-full md:w-1/2"},null,8,["modelValue"])]),a("div",Dl,[n[82]||(n[82]=a("label",null,"Chat IDs (Kommagetrennt)",-1)),d(s(w),{modelValue:Y.value,"onUpdate:modelValue":n[22]||(n[22]=r=>Y.value=r),class:"w-full md:w-1/2"},null,8,["modelValue"])])])):k("",!0)]),_:1}),d(s(I),{legend:"Discord",toggleable:!0},{legend:y(()=>[a("div",Ul,[d(s(_),{modelValue:e.value.discord.enabled,"onUpdate:modelValue":n[23]||(n[23]=r=>e.value.discord.enabled=r),binary:""},null,8,["modelValue"]),n[83]||(n[83]=a("span",{class:"font-bold"},"Discord",-1))])]),default:y(()=>[e.value.discord.enabled?(b(),f("div",zl,[a("div",Ol,[n[84]||(n[84]=a("label",null,"Webhook URL",-1)),d(s(w),{modelValue:e.value.discord.webhook_url,"onUpdate:modelValue":n[24]||(n[24]=r=>e.value.discord.webhook_url=r),type:"password",class:"w-full"},null,8,["modelValue"])])])):k("",!0)]),_:1}),d(s(I),{legend:"E-Mail",toggleable:!0},{legend:y(()=>[a("div",El,[d(s(_),{modelValue:e.value.email.enabled,"onUpdate:modelValue":n[25]||(n[25]=r=>e.value.email.enabled=r),binary:""},null,8,["modelValue"]),n[85]||(n[85]=a("span",{class:"font-bold"},"E-Mail",-1))])]),default:y(()=>[e.value.email.enabled?(b(),f("div",jl,[a("div",Kl,[a("div",ql,[n[86]||(n[86]=a("label",null,"SMTP Server",-1)),d(s(w),{modelValue:e.value.email.smtp_server,"onUpdate:modelValue":n[26]||(n[26]=r=>e.value.email.smtp_server=r),class:"w-full"},null,8,["modelValue"])]),a("div",Fl,[n[87]||(n[87]=a("label",null,"Port",-1)),d(s(K),{modelValue:e.value.email.smtp_port,"onUpdate:modelValue":n[27]||(n[27]=r=>e.value.email.smtp_port=r),useGrouping:!1,class:"w-full"},null,8,["modelValue"])]),a("div",Hl,[n[88]||(n[88]=a("label",null,"Benutzername",-1)),d(s(w),{modelValue:e.value.email.username,"onUpdate:modelValue":n[28]||(n[28]=r=>e.value.email.username=r),class:"w-full"},null,8,["modelValue"])]),a("div",Nl,[n[89]||(n[89]=a("label",null,"Passwort",-1)),d(s(w),{modelValue:x.value,"onUpdate:modelValue":n[29]||(n[29]=r=>x.value=r),type:"password",class:"w-full"},null,8,["modelValue"])]),a("div",Rl,[n[90]||(n[90]=a("label",null,"Absender Adresse",-1)),d(s(w),{modelValue:e.value.email.sender,"onUpdate:modelValue":n[30]||(n[30]=r=>e.value.email.sender=r),class:"w-full"},null,8,["modelValue"])])]),a("div",Ml,[n[91]||(n[91]=a("label",null,"Empfänger (Kommagetrennt)",-1)),d(s(w),{modelValue:ee.value,"onUpdate:modelValue":n[31]||(n[31]=r=>ee.value=r),class:"w-full"},null,8,["modelValue"])])])):k("",!0)]),_:1})])]),_:1}),d(s(E),{header:"KI-Analyse"},{default:y(()=>[a("div",Wl,[d(s(I),{legend:"KI & Anomalieerkennung",toggleable:!0},{legend:y(()=>[a("div",Zl,[d(s(_),{modelValue:e.value.ai.enabled,"onUpdate:modelValue":n[32]||(n[32]=r=>e.value.ai.enabled=r),binary:""},null,8,["modelValue"]),n[92]||(n[92]=a("span",{class:"font-bold"},"KI-Analyse Status anzeigen",-1))])]),default:y(()=>[e.value.ai.enabled?(b(),f("div",Gl,[n[101]||(n[101]=a("div",{class:"bg-blue-900/20 border border-blue-600/50 p-4 rounded flex items-start gap-3"},[a("i",{class:"pi pi-info-circle text-blue-400 text-xl mt-1"}),a("div",{class:"text-sm text-blue-200"},[S(" Die Anomalieerkennung läuft nun als eigenständiger "),a("strong",null,"ml-service"),S(' Container. Er nutzt die "HalfSpaceTrees" Methode (via Python '),a("code",null,"river"),S("), um kontinuierlich aus dem Datenstrom zu lernen. ")])],-1)),a("div",Ql,[n[99]||(n[99]=a("h4",{class:"font-bold text-lg mb-2 flex items-center gap-2"},[a("i",{class:"pi pi-chart-line"}),S(" Service Status ")],-1)),B.value?(b(),f("div",Jl,[a("div",Xl,[n[93]||(n[93]=a("span",{class:"text-gray-400"},"Service:",-1)),a("span",Yl,P(B.value.service||"Unbekannt"),1)]),a("div",ea,[n[94]||(n[94]=a("span",{class:"text-gray-400"},"Status:",-1)),a("span",{class:j(["font-bold",B.value.online?"text-green-400":"text-red-400"])},P(B.value.online?"Online":"Offline / Keine Daten"),3)]),a("div",ta,[n[95]||(n[95]=a("span",{class:"text-gray-400"},"Letzter Score:",-1)),a("span",na,P(B.value.score?B.value.score.toFixed(4):"0.0000"),1)]),a("div",la,[n[96]||(n[96]=a("span",{class:"text-gray-400"},"Aktuelle Anomalie:",-1)),a("span",{class:j(["font-bold",B.value.is_anomaly?"text-red-500":"text-green-500"])},P(B.value.is_anomaly?"JA":"NEIN"),3)]),a("div",aa,[n[97]||(n[97]=a("span",{class:"text-gray-400"},"Letztes Update:",-1)),a("span",oa,P(B.value.last_update?new Date(B.value.last_update*1e3).toLocaleString():"-"),1)])])):(b(),f("div",ra,[...n[98]||(n[98]=[a("i",{class:"pi pi-spin pi-spinner mr-2"},null,-1),S(" Lade Status... ",-1)])])),n[100]||(n[100]=a("div",{class:"mt-4 text-xs text-gray-500 text-center"},[S(" Hinweis: Alarme können über Grafana konfiguriert werden (Metrik: "),a("code",null,"idm_anomaly_flag"),S("). ")],-1))])])):k("",!0)]),_:1})])]),_:1}),d(s(E),{header:"Sicherheit"},{default:y(()=>[a("div",ia,[d(s(I),{legend:"Webzugriff",toggleable:!0},{default:y(()=>[a("div",sa,[a("div",da,[n[102]||(n[102]=a("label",null,"Admin Passwort",-1)),d(s(T),{label:"Passwort ändern",icon:"pi pi-key",severity:"secondary",outlined:"",class:"w-full md:w-auto self-start",onClick:n[33]||(n[33]=r=>l.value=!0)})]),a("div",ua,[d(s(_),{modelValue:e.value.web.write_enabled,"onUpdate:modelValue":n[34]||(n[34]=r=>e.value.web.write_enabled=r),binary:"",inputId:"write_access"},null,8,["modelValue"]),n[103]||(n[103]=a("div",{class:"flex flex-col"},[a("label",{for:"write_access",class:"font-bold cursor-pointer"},"Schreibzugriff erlauben"),a("span",{class:"text-sm text-gray-400"},"Erforderlich für manuelle Steuerung und Zeitpläne")],-1))])])]),_:1}),d(s(I),{legend:"Netzwerk Firewall",toggleable:!0},{legend:y(()=>[a("div",ca,[d(s(_),{modelValue:e.value.network_security.enabled,"onUpdate:modelValue":n[35]||(n[35]=r=>e.value.network_security.enabled=r),binary:""},null,8,["modelValue"]),n[104]||(n[104]=a("span",{class:"font-bold"},"IP Whitelist/Blacklist",-1))])]),default:y(()=>[e.value.network_security.enabled?(b(),f("div",pa,[a("div",ba,[n[107]||(n[107]=a("i",{class:"pi pi-exclamation-triangle mt-0.5"},null,-1)),a("span",null,[n[105]||(n[105]=S("Deine IP ist ",-1)),a("strong",null,P($e.value),1),n[106]||(n[106]=S(". Füge diese zur Whitelist hinzu, sonst sperrst du dich aus!",-1))])]),a("div",fa,[a("div",ga,[n[108]||(n[108]=a("label",{class:"font-bold text-green-400"},"Whitelist (Erlaubt)",-1)),d(s(oe),{modelValue:g.value,"onUpdate:modelValue":n[36]||(n[36]=r=>g.value=r),rows:"5",class:"w-full font-mono text-sm",placeholder:"192.168.1.0/24"},null,8,["modelValue"])]),a("div",va,[n[109]||(n[109]=a("label",{class:"font-bold text-red-400"},"Blacklist (Blockiert)",-1)),d(s(oe),{modelValue:$.value,"onUpdate:modelValue":n[37]||(n[37]=r=>$.value=r),rows:"5",class:"w-full font-mono text-sm",placeholder:"1.2.3.4"},null,8,["modelValue"])])])])):k("",!0)]),_:1})])]),_:1}),d(s(E),{header:"System & Wartung"},{default:y(()=>[a("div",ma,[a("div",ya,[n[115]||(n[115]=a("h3",{class:"font-bold text-lg flex items-center gap-2"},[a("i",{class:"pi pi-refresh"}),S(" Update Status ")],-1)),a("div",ha,[a("div",null,[n[110]||(n[110]=a("div",{class:"text-sm text-gray-400"},"Installierte Version",-1)),a("div",xa,P(N.value.current_version||"v0.0.0"),1)]),a("div",wa,[n[111]||(n[111]=a("div",{class:"text-sm text-gray-400"},"Verfügbare Version",-1)),a("div",ka,P(N.value.latest_version||"Checking..."),1)])]),N.value.update_available?(b(),f("div",Va,[n[112]||(n[112]=a("div",{class:"flex items-center gap-2 text-blue-300 text-sm"},[a("i",{class:"pi pi-info-circle"}),a("span",null,"Neue Version verfügbar!")],-1)),d(s(T),{label:"Jetzt aktualisieren",icon:"pi pi-download",severity:"info",size:"small",onClick:it,loading:ge.value},null,8,["loading"])])):k("",!0),a("div",_a,[n[114]||(n[114]=a("label",{class:"text-sm font-bold"},"Update Kanal",-1)),a("div",Ta,[d(s(we),{modelValue:e.value.updates.channel,"onUpdate:modelValue":n[38]||(n[38]=r=>e.value.updates.channel=r),options:["dev","release"],allowEmpty:!1,class:"w-full"},null,8,["modelValue"])]),a("div",Pa,[a("div",$a,[d(s(_),{modelValue:e.value.updates.enabled,"onUpdate:modelValue":n[39]||(n[39]=r=>e.value.updates.enabled=r),binary:"",inputId:"auto_updates"},null,8,["modelValue"]),n[113]||(n[113]=a("label",{for:"auto_updates",class:"text-sm"},"Auto-Updates",-1))]),d(s(T),{label:"Suche Updates",icon:"pi pi-search",size:"small",onClick:Je,loading:se.value},null,8,["loading"])])])]),a("div",Sa,[n[123]||(n[123]=a("h3",{class:"font-bold text-lg flex items-center gap-2"},[a("i",{class:"pi pi-database"}),S(" Backup ")],-1)),a("div",Aa,[a("div",Ca,[a("div",Ia,[d(s(_),{modelValue:e.value.backup.enabled,"onUpdate:modelValue":n[40]||(n[40]=r=>e.value.backup.enabled=r),binary:"",inputId:"auto_backup"},null,8,["modelValue"]),n[116]||(n[116]=a("label",{for:"auto_backup",class:"font-bold text-sm"},"Automatisches Backup",-1))])]),e.value.backup.enabled?(b(),f("div",Ba,[a("div",La,[n[117]||(n[117]=a("label",{class:"text-xs text-gray-400"},"Intervall (Std)",-1)),d(s(K),{modelValue:e.value.backup.interval,"onUpdate:modelValue":n[41]||(n[41]=r=>e.value.backup.interval=r),min:1,max:168,class:"p-inputtext-sm"},null,8,["modelValue"])]),a("div",Da,[n[118]||(n[118]=a("label",{class:"text-xs text-gray-400"},"Behalten (Anzahl)",-1)),d(s(K),{modelValue:e.value.backup.retention,"onUpdate:modelValue":n[42]||(n[42]=r=>e.value.backup.retention=r),min:1,max:50,class:"p-inputtext-sm"},null,8,["modelValue"])]),a("div",Ua,[d(s(_),{modelValue:e.value.backup.auto_upload,"onUpdate:modelValue":n[43]||(n[43]=r=>e.value.backup.auto_upload=r),binary:"",inputId:"backup_upload",disabled:!e.value.webdav.enabled},null,8,["modelValue","disabled"]),a("label",{for:"backup_upload",class:j(["text-xs",{"opacity-50":!e.value.webdav.enabled}])},"Automatisch in Cloud hochladen",2)])])):k("",!0)]),a("div",za,[d(s(T),{label:"Backup erstellen",icon:"pi pi-download",size:"small",onClick:et,loading:pe.value},null,8,["loading"]),d(s(T),{label:"Backup hochladen",icon:"pi pi-upload",size:"small",severity:"secondary",onClick:n[44]||(n[44]=r=>u.$refs.fileInput.click())}),a("input",{type:"file",ref_key:"fileInput",ref:be,class:"hidden",onChange:at,accept:".zip"},null,544)]),R.value?(b(),O(s(T),{key:0,label:"Wiederherstellen starten",severity:"warning",class:"w-full mt-2",onClick:ot})):k("",!0),a("div",Oa,[(b(!0),f(U,null,F(Ae.value,r=>(b(),f("div",{key:r.filename,class:"flex justify-between items-center p-2 hover:bg-gray-700 rounded text-sm border-b border-gray-700 last:border-0"},[a("span",Ea,P(r.filename),1),a("div",ja,[d(s(T),{icon:"pi pi-cloud-upload",text:"",size:"small",onClick:A=>nt(r.filename),title:"Upload to WebDAV"},null,8,["onClick"]),d(s(T),{icon:"pi pi-download",text:"",size:"small",onClick:A=>tt(r.filename)},null,8,["onClick"]),d(s(T),{icon:"pi pi-trash",text:"",severity:"danger",size:"small",onClick:A=>lt(r.filename)},null,8,["onClick"])])]))),128))]),a("div",Ka,[a("div",qa,[d(s(_),{modelValue:e.value.webdav.enabled,"onUpdate:modelValue":n[45]||(n[45]=r=>e.value.webdav.enabled=r),binary:"",inputId:"webdav_enabled"},null,8,["modelValue"]),n[119]||(n[119]=a("label",{for:"webdav_enabled",class:"font-bold cursor-pointer"},"Cloud Backup (WebDAV/Nextcloud)",-1))]),e.value.webdav.enabled?(b(),f("div",Fa,[a("div",Ha,[n[120]||(n[120]=a("label",{class:"text-xs"},"URL",-1)),d(s(w),{modelValue:e.value.webdav.url,"onUpdate:modelValue":n[46]||(n[46]=r=>e.value.webdav.url=r),placeholder:"https://cloud.example.com/remote.php/dav/files/user/",class:"p-inputtext-sm w-full"},null,8,["modelValue"])]),a("div",Na,[n[121]||(n[121]=a("label",{class:"text-xs"},"Benutzername",-1)),d(s(w),{modelValue:e.value.webdav.username,"onUpdate:modelValue":n[47]||(n[47]=r=>e.value.webdav.username=r),class:"p-inputtext-sm w-full"},null,8,["modelValue"])]),a("div",Ra,[n[122]||(n[122]=a("label",{class:"text-xs"},"Passwort",-1)),d(s(w),{modelValue:p.value,"onUpdate:modelValue":n[48]||(n[48]=r=>p.value=r),type:"password",class:"p-inputtext-sm w-full"},null,8,["modelValue"])])])):k("",!0)])]),a("div",Ma,[n[124]||(n[124]=a("h3",{class:"font-bold text-lg flex items-center gap-2 text-red-400"},[a("i",{class:"pi pi-power-off"}),S(" Danger Zone ")],-1)),a("div",Wa,[d(s(T),{label:"Dienst neu starten",icon:"pi pi-refresh",severity:"warning",onClick:Ye}),d(s(T),{label:"Datenbank löschen",icon:"pi pi-trash",severity:"danger",onClick:n[49]||(n[49]=r=>M.value=!0)})])])])]),_:1})]),_:1})])),a("div",Za,[d(s(T),{label:"Speichern",icon:"pi pi-save",onClick:De,loading:de.value,size:"large",severity:"primary"},null,8,["loading"])]),d(s(Ee),{visible:l.value,"onUpdate:visible":n[53]||(n[53]=r=>l.value=r),modal:"",header:"Passwort ändern",style:{width:"400px"}},{footer:y(()=>[d(s(T),{label:"Abbrechen",text:"",onClick:n[52]||(n[52]=r=>l.value=!1)}),d(s(T),{label:"Speichern",onClick:Xe,disabled:!o.value||!c.value||ce.value},null,8,["disabled"])]),default:y(()=>[a("div",Ga,[a("div",Qa,[n[125]||(n[125]=a("label",null,"Neues Passwort",-1)),d(s(w),{modelValue:o.value,"onUpdate:modelValue":n[50]||(n[50]=r=>o.value=r),type:"password",class:"w-full"},null,8,["modelValue"])]),a("div",Ja,[n[126]||(n[126]=a("label",null,"Bestätigen",-1)),d(s(w),{modelValue:c.value,"onUpdate:modelValue":n[51]||(n[51]=r=>c.value=r),type:"password",class:j(["w-full",{"p-invalid":ce.value}])},null,8,["modelValue","class"]),ce.value?(b(),f("small",Xa,"Passwörter stimmen nicht überein")):k("",!0)])])]),_:1},8,["visible"]),d(s(Ee),{visible:M.value,"onUpdate:visible":n[56]||(n[56]=r=>M.value=r),modal:"",header:"Datenbank löschen",style:{width:"450px"}},{footer:y(()=>[d(s(T),{label:"Abbrechen",text:"",onClick:n[55]||(n[55]=r=>M.value=!1)}),d(s(T),{label:"Alles löschen",severity:"danger",onClick:rt,disabled:W.value!=="DELETE",loading:fe.value},null,8,["disabled","loading"])]),default:y(()=>[a("div",Ya,[n[127]||(n[127]=a("div",{class:"flex items-start gap-3"},[a("i",{class:"pi pi-exclamation-triangle text-red-500 text-2xl"}),a("div",{class:"flex flex-col gap-2"},[a("span",{class:"font-bold text-lg"},"Bist du dir absolut sicher?"),a("p",{class:"text-gray-300"},[S(" Diese Aktion löscht "),a("span",{class:"font-bold text-red-400"},"ALLE"),S(" Daten dauerhaft aus der Datenbank. ")])])],-1)),d(s(w),{modelValue:W.value,"onUpdate:modelValue":n[54]||(n[54]=r=>W.value=r),placeholder:"Tippe DELETE",class:"w-full"},null,8,["modelValue"])])]),_:1},8,["visible"]),d(s(ht)),d(s(xt))]))}};export{co as default};
