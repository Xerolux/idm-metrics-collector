import{a as g,o as b,f as i,m as v,B as K,l as ge,b as c,p as B,h as x,q as z,t as S,n as ve,g as O,s as j,w as m,ag as he,T as Ye,aa as M,ah as Ae,D as Qe,A as $e,ai as N,F as D,x as H,X as J,z as Ve,a5 as G,k as Ge,a6 as Je,aj as et,ak as tt,al as nt,r as w,v as at,U as lt,N as rt,y as k,d as p,j as E}from"./index-ahQJ4VuN.js";import{a as it,s as $}from"./index-DeWQBTLg.js";import{b as me,R as te,a as ye,f as Q,s as V}from"./index-CfUEBMLz.js";import{a as ot,b as we,s as C}from"./index-C4rgdjEW.js";import{s as se}from"./index-wieK11ba.js";import{s as st}from"./index-Cq0Owdn7.js";import{s as dt}from"./index-BoH5UJjb.js";import{s as ut}from"./index-DSrt-riM.js";import{_ as ct}from"./TechnicianCodeGenerator-BwRH43lO.js";import"./index-Bs_7I09D.js";import"./index-BASSk_b3.js";var De={name:"PlusIcon",extends:me};function pt(t){return vt(t)||gt(t)||bt(t)||ft()}function ft(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function bt(t,e){if(t){if(typeof t=="string")return de(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?de(t,e):void 0}}function gt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function vt(t){if(Array.isArray(t))return de(t)}function de(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,a=Array(e);n<e;n++)a[n]=t[n];return a}function ht(t,e,n,a,o,r){return b(),g("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),pt(e[0]||(e[0]=[i("path",{d:"M7.67742 6.32258V0.677419C7.67742 0.497757 7.60605 0.325452 7.47901 0.198411C7.35197 0.0713707 7.17966 0 7 0C6.82034 0 6.64803 0.0713707 6.52099 0.198411C6.39395 0.325452 6.32258 0.497757 6.32258 0.677419V6.32258H0.677419C0.497757 6.32258 0.325452 6.39395 0.198411 6.52099C0.0713707 6.64803 0 6.82034 0 7C0 7.17966 0.0713707 7.35197 0.198411 7.47901C0.325452 7.60605 0.497757 7.67742 0.677419 7.67742H6.32258V13.3226C6.32492 13.5015 6.39704 13.6725 6.52358 13.799C6.65012 13.9255 6.82106 13.9977 7 14C7.17966 14 7.35197 13.9286 7.47901 13.8016C7.60605 13.6745 7.67742 13.5022 7.67742 13.3226V7.67742H13.3226C13.5022 7.67742 13.6745 7.60605 13.8016 7.47901C13.9286 7.35197 14 7.17966 14 7C13.9977 6.82106 13.9255 6.65012 13.799 6.52358C13.6725 6.39704 13.5015 6.32492 13.3226 6.32258H7.67742Z",fill:"currentColor"},null,-1)])),16)}De.render=ht;var mt=`
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
`,yt={root:function(e){var n=e.props;return["p-fieldset p-component",{"p-fieldset-toggleable":n.toggleable}]},legend:"p-fieldset-legend",legendLabel:"p-fieldset-legend-label",toggleButton:"p-fieldset-toggle-button",toggleIcon:"p-fieldset-toggle-icon",contentContainer:"p-fieldset-content-container",contentWrapper:"p-fieldset-content-wrapper",content:"p-fieldset-content"},wt=K.extend({name:"fieldset",style:mt,classes:yt}),xt={name:"BaseFieldset",extends:ye,props:{legend:String,toggleable:Boolean,collapsed:Boolean,toggleButtonProps:{type:null,default:null}},style:wt,provide:function(){return{$pcFieldset:this,$parentInstance:this}}},I={name:"Fieldset",extends:xt,inheritAttrs:!1,emits:["update:collapsed","toggle"],data:function(){return{d_collapsed:this.collapsed}},watch:{collapsed:function(e){this.d_collapsed=e}},methods:{toggle:function(e){this.d_collapsed=!this.d_collapsed,this.$emit("update:collapsed",this.d_collapsed),this.$emit("toggle",{originalEvent:e,value:this.d_collapsed})},onKeyDown:function(e){(e.code==="Enter"||e.code==="NumpadEnter"||e.code==="Space")&&(this.toggle(e),e.preventDefault())}},computed:{buttonAriaLabel:function(){return this.toggleButtonProps&&this.toggleButtonProps.ariaLabel?this.toggleButtonProps.ariaLabel:this.legend},dataP:function(){return Q({toggleable:this.toggleable})}},directives:{ripple:te},components:{PlusIcon:De,MinusIcon:it}};function R(t){"@babel/helpers - typeof";return R=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},R(t)}function Be(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);e&&(a=a.filter(function(o){return Object.getOwnPropertyDescriptor(t,o).enumerable})),n.push.apply(n,a)}return n}function Ce(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?Be(Object(n),!0).forEach(function(a){kt(t,a,n[a])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):Be(Object(n)).forEach(function(a){Object.defineProperty(t,a,Object.getOwnPropertyDescriptor(n,a))})}return t}function kt(t,e,n){return(e=Pt(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Pt(t){var e=St(t,"string");return R(e)=="symbol"?e:e+""}function St(t,e){if(R(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(R(a)!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var Tt=["data-p"],At=["data-p"],$t=["id"],Vt=["id","aria-controls","aria-expanded","aria-label"],Bt=["id","aria-labelledby"];function Ct(t,e,n,a,o,r){var d=ge("ripple");return b(),g("fieldset",v({class:t.cx("root"),"data-p":r.dataP},t.ptmi("root")),[i("legend",v({class:t.cx("legend"),"data-p":r.dataP},t.ptm("legend")),[B(t.$slots,"legend",{toggleCallback:r.toggle},function(){return[t.toggleable?x("",!0):(b(),g("span",v({key:0,id:t.$id+"_header",class:t.cx("legendLabel")},t.ptm("legendLabel")),S(t.legend),17,$t)),t.toggleable?z((b(),g("button",v({key:1,id:t.$id+"_header",type:"button","aria-controls":t.$id+"_content","aria-expanded":!o.d_collapsed,"aria-label":r.buttonAriaLabel,class:t.cx("toggleButton"),onClick:e[0]||(e[0]=function(){return r.toggle&&r.toggle.apply(r,arguments)}),onKeydown:e[1]||(e[1]=function(){return r.onKeyDown&&r.onKeyDown.apply(r,arguments)})},Ce(Ce({},t.toggleButtonProps),t.ptm("toggleButton"))),[B(t.$slots,t.$slots.toggleicon?"toggleicon":"togglericon",{collapsed:o.d_collapsed,class:ve(t.cx("toggleIcon"))},function(){return[(b(),O(j(o.d_collapsed?"PlusIcon":"MinusIcon"),v({class:t.cx("toggleIcon")},t.ptm("toggleIcon")),null,16,["class"]))]}),i("span",v({class:t.cx("legendLabel")},t.ptm("legendLabel")),S(t.legend),17)],16,Vt)),[[d]]):x("",!0)]})],16,At),c(Ye,v({name:"p-collapsible"},t.ptm("transition")),{default:m(function(){return[z(i("div",v({id:t.$id+"_content",class:t.cx("contentContainer"),role:"region","aria-labelledby":t.$id+"_header"},t.ptm("contentContainer")),[i("div",v({class:t.cx("contentWrapper")},t.ptm("contentWrapper")),[i("div",v({class:t.cx("content")},t.ptm("content")),[B(t.$slots,"default")],16)],16)],16,Bt),[[he,!o.d_collapsed]])]}),_:3},16)],16,Tt)}I.render=Ct;var It=`
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
`,Dt={root:function(e){var n=e.instance,a=e.props;return["p-textarea p-component",{"p-filled":n.$filled,"p-textarea-resizable ":a.autoResize,"p-textarea-sm p-inputfield-sm":a.size==="small","p-textarea-lg p-inputfield-lg":a.size==="large","p-invalid":n.$invalid,"p-variant-filled":n.$variant==="filled","p-textarea-fluid":n.$fluid}]}},Lt=K.extend({name:"textarea",style:It,classes:Dt}),Et={name:"BaseTextarea",extends:ot,props:{autoResize:Boolean},style:Lt,provide:function(){return{$pcTextarea:this,$parentInstance:this}}};function W(t){"@babel/helpers - typeof";return W=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},W(t)}function zt(t,e,n){return(e=Ot(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Ot(t){var e=_t(t,"string");return W(e)=="symbol"?e:e+""}function _t(t,e){if(W(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(W(a)!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var ee={name:"Textarea",extends:Et,inheritAttrs:!1,observer:null,mounted:function(){var e=this;this.autoResize&&(this.observer=new ResizeObserver(function(){requestAnimationFrame(function(){e.resize()})}),this.observer.observe(this.$el))},updated:function(){this.autoResize&&this.resize()},beforeUnmount:function(){this.observer&&this.observer.disconnect()},methods:{resize:function(){if(this.$el.offsetParent){var e=this.$el.style.height,n=parseInt(e)||0,a=this.$el.scrollHeight,o=!n||a>n,r=n&&a<n;r?(this.$el.style.height="auto",this.$el.style.height="".concat(this.$el.scrollHeight,"px")):o&&(this.$el.style.height="".concat(a,"px"))}},onInput:function(e){this.autoResize&&this.resize(),this.writeValue(e.target.value,e)}},computed:{attrs:function(){return v(this.ptmi("root",{context:{filled:this.$filled,disabled:this.disabled}}),this.formField)},dataP:function(){return Q(zt({invalid:this.$invalid,fluid:this.$fluid,filled:this.$variant==="filled"},this.size,this.size))}}},Kt=["value","name","disabled","aria-invalid","data-p"];function jt(t,e,n,a,o,r){return b(),g("textarea",v({class:t.cx("root"),value:t.d_value,name:t.name,disabled:t.disabled,"aria-invalid":t.invalid||void 0,"data-p":r.dataP,onInput:e[0]||(e[0]=function(){return r.onInput&&r.onInput.apply(r,arguments)})},r.attrs),null,16,Kt)}ee.render=jt;var Le={name:"ChevronLeftIcon",extends:me};function Ht(t){return Mt(t)||Ft(t)||Ut(t)||qt()}function qt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Ut(t,e){if(t){if(typeof t=="string")return ue(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?ue(t,e):void 0}}function Ft(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Mt(t){if(Array.isArray(t))return ue(t)}function ue(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,a=Array(e);n<e;n++)a[n]=t[n];return a}function Nt(t,e,n,a,o,r){return b(),g("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Ht(e[0]||(e[0]=[i("path",{d:"M9.61296 13C9.50997 13.0005 9.40792 12.9804 9.3128 12.9409C9.21767 12.9014 9.13139 12.8433 9.05902 12.7701L3.83313 7.54416C3.68634 7.39718 3.60388 7.19795 3.60388 6.99022C3.60388 6.78249 3.68634 6.58325 3.83313 6.43628L9.05902 1.21039C9.20762 1.07192 9.40416 0.996539 9.60724 1.00012C9.81032 1.00371 10.0041 1.08597 10.1477 1.22959C10.2913 1.37322 10.3736 1.56698 10.3772 1.77005C10.3808 1.97313 10.3054 2.16968 10.1669 2.31827L5.49496 6.99022L10.1669 11.6622C10.3137 11.8091 10.3962 12.0084 10.3962 12.2161C10.3962 12.4238 10.3137 12.6231 10.1669 12.7701C10.0945 12.8433 10.0083 12.9014 9.91313 12.9409C9.81801 12.9804 9.71596 13.0005 9.61296 13Z",fill:"currentColor"},null,-1)])),16)}Le.render=Nt;var Ee={name:"ChevronRightIcon",extends:me};function Rt(t){return Yt(t)||Xt(t)||Zt(t)||Wt()}function Wt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Zt(t,e){if(t){if(typeof t=="string")return ce(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?ce(t,e):void 0}}function Xt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Yt(t){if(Array.isArray(t))return ce(t)}function ce(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,a=Array(e);n<e;n++)a[n]=t[n];return a}function Qt(t,e,n,a,o,r){return b(),g("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Rt(e[0]||(e[0]=[i("path",{d:"M4.38708 13C4.28408 13.0005 4.18203 12.9804 4.08691 12.9409C3.99178 12.9014 3.9055 12.8433 3.83313 12.7701C3.68634 12.6231 3.60388 12.4238 3.60388 12.2161C3.60388 12.0084 3.68634 11.8091 3.83313 11.6622L8.50507 6.99022L3.83313 2.31827C3.69467 2.16968 3.61928 1.97313 3.62287 1.77005C3.62645 1.56698 3.70872 1.37322 3.85234 1.22959C3.99596 1.08597 4.18972 1.00371 4.3928 1.00012C4.59588 0.996539 4.79242 1.07192 4.94102 1.21039L10.1669 6.43628C10.3137 6.58325 10.3962 6.78249 10.3962 6.99022C10.3962 7.19795 10.3137 7.39718 10.1669 7.54416L4.94102 12.7701C4.86865 12.8433 4.78237 12.9014 4.68724 12.9409C4.59212 12.9804 4.49007 13.0005 4.38708 13Z",fill:"currentColor"},null,-1)])),16)}Ee.render=Qt;var Gt=`
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
`,Jt={root:function(e){var n=e.props;return["p-tabview p-component",{"p-tabview-scrollable":n.scrollable}]},navContainer:"p-tabview-tablist-container",prevButton:"p-tabview-prev-button",navContent:"p-tabview-tablist-scroll-container",nav:"p-tabview-tablist",tab:{header:function(e){var n=e.instance,a=e.tab,o=e.index;return["p-tabview-tablist-item",n.getTabProp(a,"headerClass"),{"p-tabview-tablist-item-active":n.d_activeIndex===o,"p-disabled":n.getTabProp(a,"disabled")}]},headerAction:"p-tabview-tab-header",headerTitle:"p-tabview-tab-title",content:function(e){var n=e.instance,a=e.tab;return["p-tabview-panel",n.getTabProp(a,"contentClass")]}},inkbar:"p-tabview-ink-bar",nextButton:"p-tabview-next-button",panelContainer:"p-tabview-panels"},en=K.extend({name:"tabview",style:Gt,classes:Jt}),tn={name:"BaseTabView",extends:ye,props:{activeIndex:{type:Number,default:0},lazy:{type:Boolean,default:!1},scrollable:{type:Boolean,default:!1},tabindex:{type:Number,default:0},selectOnFocus:{type:Boolean,default:!1},prevButtonProps:{type:null,default:null},nextButtonProps:{type:null,default:null},prevIcon:{type:String,default:void 0},nextIcon:{type:String,default:void 0}},style:en,provide:function(){return{$pcTabs:void 0,$pcTabView:this,$parentInstance:this}}},ze={name:"TabView",extends:tn,inheritAttrs:!1,emits:["update:activeIndex","tab-change","tab-click"],data:function(){return{d_activeIndex:this.activeIndex,isPrevButtonDisabled:!0,isNextButtonDisabled:!1}},watch:{activeIndex:function(e){this.d_activeIndex=e,this.scrollInView({index:e})}},mounted:function(){console.warn("Deprecated since v4. Use Tabs component instead."),this.updateInkBar(),this.scrollable&&this.updateButtonState()},updated:function(){this.updateInkBar(),this.scrollable&&this.updateButtonState()},methods:{isTabPanel:function(e){return e.type.name==="TabPanel"},isTabActive:function(e){return this.d_activeIndex===e},getTabProp:function(e,n){return e.props?e.props[n]:void 0},getKey:function(e,n){return this.getTabProp(e,"header")||n},getTabHeaderActionId:function(e){return"".concat(this.$id,"_").concat(e,"_header_action")},getTabContentId:function(e){return"".concat(this.$id,"_").concat(e,"_content")},getTabPT:function(e,n,a){var o=this.tabs.length,r={props:e.props,parent:{instance:this,props:this.$props,state:this.$data},context:{index:a,count:o,first:a===0,last:a===o-1,active:this.isTabActive(a)}};return v(this.ptm("tabpanel.".concat(n),{tabpanel:r}),this.ptm("tabpanel.".concat(n),r),this.ptmo(this.getTabProp(e,"pt"),n,r))},onScroll:function(e){this.scrollable&&this.updateButtonState(),e.preventDefault()},onPrevButtonClick:function(){var e=this.$refs.content,n=M(e),a=e.scrollLeft-n;e.scrollLeft=a<=0?0:a},onNextButtonClick:function(){var e=this.$refs.content,n=M(e)-this.getVisibleButtonWidths(),a=e.scrollLeft+n,o=e.scrollWidth-n;e.scrollLeft=a>=o?o:a},onTabClick:function(e,n,a){this.changeActiveIndex(e,n,a),this.$emit("tab-click",{originalEvent:e,index:a})},onTabKeyDown:function(e,n,a){switch(e.code){case"ArrowLeft":this.onTabArrowLeftKey(e);break;case"ArrowRight":this.onTabArrowRightKey(e);break;case"Home":this.onTabHomeKey(e);break;case"End":this.onTabEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":case"Space":this.onTabEnterKey(e,n,a);break}},onTabArrowRightKey:function(e){var n=this.findNextHeaderAction(e.target.parentElement);n?this.changeFocusedTab(e,n):this.onTabHomeKey(e),e.preventDefault()},onTabArrowLeftKey:function(e){var n=this.findPrevHeaderAction(e.target.parentElement);n?this.changeFocusedTab(e,n):this.onTabEndKey(e),e.preventDefault()},onTabHomeKey:function(e){var n=this.findFirstHeaderAction();this.changeFocusedTab(e,n),e.preventDefault()},onTabEndKey:function(e){var n=this.findLastHeaderAction();this.changeFocusedTab(e,n),e.preventDefault()},onPageDownKey:function(e){this.scrollInView({index:this.$refs.nav.children.length-2}),e.preventDefault()},onPageUpKey:function(e){this.scrollInView({index:0}),e.preventDefault()},onTabEnterKey:function(e,n,a){this.changeActiveIndex(e,n,a),e.preventDefault()},findNextHeaderAction:function(e){var n=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,a=n?e:e.nextElementSibling;return a?N(a,"data-p-disabled")||N(a,"data-pc-section")==="inkbar"?this.findNextHeaderAction(a):$e(a,'[data-pc-section="headeraction"]'):null},findPrevHeaderAction:function(e){var n=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,a=n?e:e.previousElementSibling;return a?N(a,"data-p-disabled")||N(a,"data-pc-section")==="inkbar"?this.findPrevHeaderAction(a):$e(a,'[data-pc-section="headeraction"]'):null},findFirstHeaderAction:function(){return this.findNextHeaderAction(this.$refs.nav.firstElementChild,!0)},findLastHeaderAction:function(){return this.findPrevHeaderAction(this.$refs.nav.lastElementChild,!0)},changeActiveIndex:function(e,n,a){!this.getTabProp(n,"disabled")&&this.d_activeIndex!==a&&(this.d_activeIndex=a,this.$emit("update:activeIndex",a),this.$emit("tab-change",{originalEvent:e,index:a}),this.scrollInView({index:a}))},changeFocusedTab:function(e,n){if(n&&(Qe(n),this.scrollInView({element:n}),this.selectOnFocus)){var a=parseInt(n.parentElement.dataset.pcIndex,10),o=this.tabs[a];this.changeActiveIndex(e,o,a)}},scrollInView:function(e){var n=e.element,a=e.index,o=a===void 0?-1:a,r=n||this.$refs.nav.children[o];r&&r.scrollIntoView&&r.scrollIntoView({block:"nearest"})},updateInkBar:function(){var e=this.$refs.nav.children[this.d_activeIndex];this.$refs.inkbar.style.width=M(e)+"px",this.$refs.inkbar.style.left=Ae(e).left-Ae(this.$refs.nav).left+"px"},updateButtonState:function(){var e=this.$refs.content,n=e.scrollLeft,a=e.scrollWidth,o=M(e);this.isPrevButtonDisabled=n===0,this.isNextButtonDisabled=parseInt(n)===a-o},getVisibleButtonWidths:function(){var e=this.$refs,n=e.prevBtn,a=e.nextBtn;return[n,a].reduce(function(o,r){return r?o+M(r):o},0)}},computed:{tabs:function(){var e=this;return this.$slots.default().reduce(function(n,a){return e.isTabPanel(a)?n.push(a):a.children&&a.children instanceof Array&&a.children.forEach(function(o){e.isTabPanel(o)&&n.push(o)}),n},[])},prevButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.previous:void 0},nextButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.next:void 0}},directives:{ripple:te},components:{ChevronLeftIcon:Le,ChevronRightIcon:Ee}};function Z(t){"@babel/helpers - typeof";return Z=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},Z(t)}function Ie(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);e&&(a=a.filter(function(o){return Object.getOwnPropertyDescriptor(t,o).enumerable})),n.push.apply(n,a)}return n}function P(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?Ie(Object(n),!0).forEach(function(a){nn(t,a,n[a])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):Ie(Object(n)).forEach(function(a){Object.defineProperty(t,a,Object.getOwnPropertyDescriptor(n,a))})}return t}function nn(t,e,n){return(e=an(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function an(t){var e=ln(t,"string");return Z(e)=="symbol"?e:e+""}function ln(t,e){if(Z(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(Z(a)!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var rn=["tabindex","aria-label"],on=["data-p-active","data-p-disabled","data-pc-index"],sn=["id","tabindex","aria-disabled","aria-selected","aria-controls","onClick","onKeydown"],dn=["tabindex","aria-label"],un=["id","aria-labelledby","data-pc-index","data-p-active"];function cn(t,e,n,a,o,r){var d=ge("ripple");return b(),g("div",v({class:t.cx("root"),role:"tablist"},t.ptmi("root")),[i("div",v({class:t.cx("navContainer")},t.ptm("navContainer")),[t.scrollable&&!o.isPrevButtonDisabled?z((b(),g("button",v({key:0,ref:"prevBtn",type:"button",class:t.cx("prevButton"),tabindex:t.tabindex,"aria-label":r.prevButtonAriaLabel,onClick:e[0]||(e[0]=function(){return r.onPrevButtonClick&&r.onPrevButtonClick.apply(r,arguments)})},P(P({},t.prevButtonProps),t.ptm("prevButton")),{"data-pc-group-section":"navbutton"}),[B(t.$slots,"previcon",{},function(){return[(b(),O(j(t.prevIcon?"span":"ChevronLeftIcon"),v({"aria-hidden":"true",class:t.prevIcon},t.ptm("prevIcon")),null,16,["class"]))]})],16,rn)),[[d]]):x("",!0),i("div",v({ref:"content",class:t.cx("navContent"),onScroll:e[1]||(e[1]=function(){return r.onScroll&&r.onScroll.apply(r,arguments)})},t.ptm("navContent")),[i("ul",v({ref:"nav",class:t.cx("nav")},t.ptm("nav")),[(b(!0),g(D,null,H(r.tabs,function(u,h){return b(),g("li",v({key:r.getKey(u,h),style:r.getTabProp(u,"headerStyle"),class:t.cx("tab.header",{tab:u,index:h}),role:"presentation"},{ref_for:!0},P(P(P({},r.getTabProp(u,"headerProps")),r.getTabPT(u,"root",h)),r.getTabPT(u,"header",h)),{"data-pc-name":"tabpanel","data-p-active":o.d_activeIndex===h,"data-p-disabled":r.getTabProp(u,"disabled"),"data-pc-index":h}),[z((b(),g("a",v({id:r.getTabHeaderActionId(h),class:t.cx("tab.headerAction"),tabindex:r.getTabProp(u,"disabled")||!r.isTabActive(h)?-1:t.tabindex,role:"tab","aria-disabled":r.getTabProp(u,"disabled"),"aria-selected":r.isTabActive(h),"aria-controls":r.getTabContentId(h),onClick:function(L){return r.onTabClick(L,u,h)},onKeydown:function(L){return r.onTabKeyDown(L,u,h)}},{ref_for:!0},P(P({},r.getTabProp(u,"headerActionProps")),r.getTabPT(u,"headerAction",h))),[u.props&&u.props.header?(b(),g("span",v({key:0,class:t.cx("tab.headerTitle")},{ref_for:!0},r.getTabPT(u,"headerTitle",h)),S(u.props.header),17)):x("",!0),u.children&&u.children.header?(b(),O(j(u.children.header),{key:1})):x("",!0)],16,sn)),[[d]])],16,on)}),128)),i("li",v({ref:"inkbar",class:t.cx("inkbar"),role:"presentation","aria-hidden":"true"},t.ptm("inkbar")),null,16)],16)],16),t.scrollable&&!o.isNextButtonDisabled?z((b(),g("button",v({key:1,ref:"nextBtn",type:"button",class:t.cx("nextButton"),tabindex:t.tabindex,"aria-label":r.nextButtonAriaLabel,onClick:e[2]||(e[2]=function(){return r.onNextButtonClick&&r.onNextButtonClick.apply(r,arguments)})},P(P({},t.nextButtonProps),t.ptm("nextButton")),{"data-pc-group-section":"navbutton"}),[B(t.$slots,"nexticon",{},function(){return[(b(),O(j(t.nextIcon?"span":"ChevronRightIcon"),v({"aria-hidden":"true",class:t.nextIcon},t.ptm("nextIcon")),null,16,["class"]))]})],16,dn)),[[d]]):x("",!0)],16),i("div",v({class:t.cx("panelContainer")},t.ptm("panelContainer")),[(b(!0),g(D,null,H(r.tabs,function(u,h){return b(),g(D,{key:r.getKey(u,h)},[!t.lazy||r.isTabActive(h)?z((b(),g("div",v({key:0,id:r.getTabContentId(h),style:r.getTabProp(u,"contentStyle"),class:t.cx("tab.content",{tab:u}),role:"tabpanel","aria-labelledby":r.getTabHeaderActionId(h)},{ref_for:!0},P(P(P({},r.getTabProp(u,"contentProps")),r.getTabPT(u,"root",h)),r.getTabPT(u,"content",h)),{"data-pc-name":"tabpanel","data-pc-index":h,"data-p-active":o.d_activeIndex===h}),[(b(),O(j(u)))],16,un)),[[he,t.lazy?!0:r.isTabActive(h)]]):x("",!0)],64)}),128))],16)],16)}ze.render=cn;var pn={root:function(e){var n=e.instance;return["p-tabpanel",{"p-tabpanel-active":n.active}]}},fn=K.extend({name:"tabpanel",classes:pn}),bn={name:"BaseTabPanel",extends:ye,props:{value:{type:[String,Number],default:void 0},as:{type:[String,Object],default:"DIV"},asChild:{type:Boolean,default:!1},header:null,headerStyle:null,headerClass:null,headerProps:null,headerActionProps:null,contentStyle:null,contentClass:null,contentProps:null,disabled:Boolean},style:fn,provide:function(){return{$pcTabPanel:this,$parentInstance:this}}},_={name:"TabPanel",extends:bn,inheritAttrs:!1,inject:["$pcTabs"],computed:{active:function(){var e;return J((e=this.$pcTabs)===null||e===void 0?void 0:e.d_value,this.value)},id:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tabpanel_").concat(this.value)},ariaLabelledby:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tab_").concat(this.value)},attrs:function(){return v(this.a11yAttrs,this.ptmi("root",this.ptParams))},a11yAttrs:function(){var e;return{id:this.id,tabindex:(e=this.$pcTabs)===null||e===void 0?void 0:e.tabindex,role:"tabpanel","aria-labelledby":this.ariaLabelledby,"data-pc-name":"tabpanel","data-p-active":this.active}},ptParams:function(){return{context:{active:this.active}}}}};function gn(t,e,n,a,o,r){var d,u;return r.$pcTabs?(b(),g(D,{key:1},[t.asChild?B(t.$slots,"default",{key:1,class:ve(t.cx("root")),active:r.active,a11yAttrs:r.a11yAttrs}):(b(),g(D,{key:0},[!((d=r.$pcTabs)!==null&&d!==void 0&&d.lazy)||r.active?z((b(),O(j(t.as),v({key:0,class:t.cx("root")},r.attrs),{default:m(function(){return[B(t.$slots,"default")]}),_:3},16,["class"])),[[he,(u=r.$pcTabs)!==null&&u!==void 0&&u.lazy?!0:r.active]]):x("",!0)],64))],64)):B(t.$slots,"default",{key:0})}_.render=gn;var vn=`
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
`,hn={root:function(e){var n=e.instance,a=e.props;return["p-togglebutton p-component",{"p-togglebutton-checked":n.active,"p-invalid":n.$invalid,"p-togglebutton-fluid":a.fluid,"p-togglebutton-sm p-inputfield-sm":a.size==="small","p-togglebutton-lg p-inputfield-lg":a.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},mn=K.extend({name:"togglebutton",style:vn,classes:hn}),yn={name:"BaseToggleButton",extends:we,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:mn,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}};function X(t){"@babel/helpers - typeof";return X=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},X(t)}function wn(t,e,n){return(e=xn(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function xn(t){var e=kn(t,"string");return X(e)=="symbol"?e:e+""}function kn(t,e){if(X(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(X(a)!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var Oe={name:"ToggleButton",extends:yn,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(e){var n=e==="root"?this.ptmi:this.ptm;return n(e,{context:{active:this.active,disabled:this.disabled}})},onChange:function(e){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,e),this.$emit("change",e))},onBlur:function(e){var n,a;(n=(a=this.formField).onBlur)===null||n===void 0||n.call(a,e)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return Ve(this.onLabel)&&Ve(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "},dataP:function(){return Q(wn({checked:this.active,invalid:this.$invalid},this.size,this.size))}},directives:{ripple:te}},Pn=["tabindex","disabled","aria-pressed","aria-label","aria-labelledby","data-p-checked","data-p-disabled","data-p"],Sn=["data-p"];function Tn(t,e,n,a,o,r){var d=ge("ripple");return z((b(),g("button",v({type:"button",class:t.cx("root"),tabindex:t.tabindex,disabled:t.disabled,"aria-pressed":t.d_value,onClick:e[0]||(e[0]=function(){return r.onChange&&r.onChange.apply(r,arguments)}),onBlur:e[1]||(e[1]=function(){return r.onBlur&&r.onBlur.apply(r,arguments)})},r.getPTOptions("root"),{"aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"data-p-checked":r.active,"data-p-disabled":t.disabled,"data-p":r.dataP}),[i("span",v({class:t.cx("content")},r.getPTOptions("content"),{"data-p":r.dataP}),[B(t.$slots,"default",{},function(){return[B(t.$slots,"icon",{value:t.d_value,class:ve(t.cx("icon"))},function(){return[t.onIcon||t.offIcon?(b(),g("span",v({key:0,class:[t.cx("icon"),t.d_value?t.onIcon:t.offIcon]},r.getPTOptions("icon")),null,16)):x("",!0)]}),i("span",v({class:t.cx("label")},r.getPTOptions("label")),S(r.label),17)]})],16,Sn)],16,Pn)),[[d]])}Oe.render=Tn;var An=`
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
`,$n={root:function(e){var n=e.props,a=e.instance;return["p-selectbutton p-component",{"p-invalid":a.$invalid,"p-selectbutton-fluid":n.fluid}]}},Vn=K.extend({name:"selectbutton",style:An,classes:$n}),Bn={name:"BaseSelectButton",extends:we,props:{options:Array,optionLabel:null,optionValue:null,optionDisabled:null,multiple:Boolean,allowEmpty:{type:Boolean,default:!0},dataKey:null,ariaLabelledby:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:Vn,provide:function(){return{$pcSelectButton:this,$parentInstance:this}}};function Cn(t,e){var n=typeof Symbol<"u"&&t[Symbol.iterator]||t["@@iterator"];if(!n){if(Array.isArray(t)||(n=_e(t))||e){n&&(t=n);var a=0,o=function(){};return{s:o,n:function(){return a>=t.length?{done:!0}:{done:!1,value:t[a++]}},e:function(T){throw T},f:o}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var r,d=!0,u=!1;return{s:function(){n=n.call(t)},n:function(){var T=n.next();return d=T.done,T},e:function(T){u=!0,r=T},f:function(){try{d||n.return==null||n.return()}finally{if(u)throw r}}}}function In(t){return En(t)||Ln(t)||_e(t)||Dn()}function Dn(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function _e(t,e){if(t){if(typeof t=="string")return pe(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?pe(t,e):void 0}}function Ln(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function En(t){if(Array.isArray(t))return pe(t)}function pe(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,a=Array(e);n<e;n++)a[n]=t[n];return a}var fe={name:"SelectButton",extends:Bn,inheritAttrs:!1,emits:["change"],methods:{getOptionLabel:function(e){return this.optionLabel?G(e,this.optionLabel):e},getOptionValue:function(e){return this.optionValue?G(e,this.optionValue):e},getOptionRenderKey:function(e){return this.dataKey?G(e,this.dataKey):this.getOptionLabel(e)},isOptionDisabled:function(e){return this.optionDisabled?G(e,this.optionDisabled):!1},isOptionReadonly:function(e){if(this.allowEmpty)return!1;var n=this.isSelected(e);return this.multiple?n&&this.d_value.length===1:n},onOptionSelect:function(e,n,a){var o=this;if(!(this.disabled||this.isOptionDisabled(n)||this.isOptionReadonly(n))){var r=this.isSelected(n),d=this.getOptionValue(n),u;if(this.multiple)if(r){if(u=this.d_value.filter(function(h){return!J(h,d,o.equalityKey)}),!this.allowEmpty&&u.length===0)return}else u=this.d_value?[].concat(In(this.d_value),[d]):[d];else{if(r&&!this.allowEmpty)return;u=r?null:d}this.writeValue(u,e),this.$emit("change",{originalEvent:e,value:u})}},isSelected:function(e){var n=!1,a=this.getOptionValue(e);if(this.multiple){if(this.d_value){var o=Cn(this.d_value),r;try{for(o.s();!(r=o.n()).done;){var d=r.value;if(J(d,a,this.equalityKey)){n=!0;break}}}catch(u){o.e(u)}finally{o.f()}}}else n=J(this.d_value,a,this.equalityKey);return n}},computed:{equalityKey:function(){return this.optionValue?null:this.dataKey},dataP:function(){return Q({invalid:this.$invalid})}},directives:{ripple:te},components:{ToggleButton:Oe}},zn=["aria-labelledby","data-p"];function On(t,e,n,a,o,r){var d=Ge("ToggleButton");return b(),g("div",v({class:t.cx("root"),role:"group","aria-labelledby":t.ariaLabelledby},t.ptmi("root"),{"data-p":r.dataP}),[(b(!0),g(D,null,H(t.options,function(u,h){return b(),O(d,{key:r.getOptionRenderKey(u),modelValue:r.isSelected(u),onLabel:r.getOptionLabel(u),offLabel:r.getOptionLabel(u),disabled:t.disabled||r.isOptionDisabled(u),unstyled:t.unstyled,size:t.size,readonly:r.isOptionReadonly(u),onChange:function(L){return r.onOptionSelect(L,u,h)},pt:t.ptm("pcToggleButton")},Je({_:2},[t.$slots.option?{name:"default",fn:m(function(){return[B(t.$slots,"option",{option:u,index:h},function(){return[i("span",v({ref_for:!0},t.ptm("pcToggleButton").label),S(r.getOptionLabel(u)),17)]})]}),key:"0"}:void 0]),1032,["modelValue","onLabel","offLabel","disabled","unstyled","size","readonly","onChange","pt"])}),128))],16,zn)}fe.render=On;var _n=`
    .p-slider {
        display: block;
        position: relative;
        background: dt('slider.track.background');
        border-radius: dt('slider.track.border.radius');
    }

    .p-slider-handle {
        cursor: grab;
        touch-action: none;
        user-select: none;
        display: flex;
        justify-content: center;
        align-items: center;
        height: dt('slider.handle.height');
        width: dt('slider.handle.width');
        background: dt('slider.handle.background');
        border-radius: dt('slider.handle.border.radius');
        transition:
            background dt('slider.transition.duration'),
            color dt('slider.transition.duration'),
            border-color dt('slider.transition.duration'),
            box-shadow dt('slider.transition.duration'),
            outline-color dt('slider.transition.duration');
        outline-color: transparent;
    }

    .p-slider-handle::before {
        content: '';
        width: dt('slider.handle.content.width');
        height: dt('slider.handle.content.height');
        display: block;
        background: dt('slider.handle.content.background');
        border-radius: dt('slider.handle.content.border.radius');
        box-shadow: dt('slider.handle.content.shadow');
        transition: background dt('slider.transition.duration');
    }

    .p-slider:not(.p-disabled) .p-slider-handle:hover {
        background: dt('slider.handle.hover.background');
    }

    .p-slider:not(.p-disabled) .p-slider-handle:hover::before {
        background: dt('slider.handle.content.hover.background');
    }

    .p-slider-handle:focus-visible {
        box-shadow: dt('slider.handle.focus.ring.shadow');
        outline: dt('slider.handle.focus.ring.width') dt('slider.handle.focus.ring.style') dt('slider.handle.focus.ring.color');
        outline-offset: dt('slider.handle.focus.ring.offset');
    }

    .p-slider-range {
        display: block;
        background: dt('slider.range.background');
        border-radius: dt('slider.track.border.radius');
    }

    .p-slider.p-slider-horizontal {
        height: dt('slider.track.size');
    }

    .p-slider-horizontal .p-slider-range {
        inset-block-start: 0;
        inset-inline-start: 0;
        height: 100%;
    }

    .p-slider-horizontal .p-slider-handle {
        inset-block-start: 50%;
        margin-block-start: calc(-1 * calc(dt('slider.handle.height') / 2));
        margin-inline-start: calc(-1 * calc(dt('slider.handle.width') / 2));
    }

    .p-slider-vertical {
        min-height: 100px;
        width: dt('slider.track.size');
    }

    .p-slider-vertical .p-slider-handle {
        inset-inline-start: 50%;
        margin-inline-start: calc(-1 * calc(dt('slider.handle.width') / 2));
        margin-block-end: calc(-1 * calc(dt('slider.handle.height') / 2));
    }

    .p-slider-vertical .p-slider-range {
        inset-block-end: 0;
        inset-inline-start: 0;
        width: 100%;
    }
`,Kn={handle:{position:"absolute"},range:{position:"absolute"}},jn={root:function(e){var n=e.instance,a=e.props;return["p-slider p-component",{"p-disabled":a.disabled,"p-invalid":n.$invalid,"p-slider-horizontal":a.orientation==="horizontal","p-slider-vertical":a.orientation==="vertical"}]},range:"p-slider-range",handle:"p-slider-handle"},Hn=K.extend({name:"slider",style:_n,classes:jn,inlineStyles:Kn}),qn={name:"BaseSlider",extends:we,props:{min:{type:Number,default:0},max:{type:Number,default:100},orientation:{type:String,default:"horizontal"},step:{type:Number,default:null},range:{type:Boolean,default:!1},tabindex:{type:Number,default:0},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null}},style:Hn,provide:function(){return{$pcSlider:this,$parentInstance:this}}};function Y(t){"@babel/helpers - typeof";return Y=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},Y(t)}function Un(t,e,n){return(e=Fn(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Fn(t){var e=Mn(t,"string");return Y(e)=="symbol"?e:e+""}function Mn(t,e){if(Y(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(Y(a)!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}function Nn(t){return Xn(t)||Zn(t)||Wn(t)||Rn()}function Rn(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Wn(t,e){if(t){if(typeof t=="string")return be(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?be(t,e):void 0}}function Zn(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Xn(t){if(Array.isArray(t))return be(t)}function be(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,a=Array(e);n<e;n++)a[n]=t[n];return a}var Ke={name:"Slider",extends:qn,inheritAttrs:!1,emits:["change","slideend"],dragging:!1,handleIndex:null,initX:null,initY:null,barWidth:null,barHeight:null,dragListener:null,dragEndListener:null,beforeUnmount:function(){this.unbindDragListeners()},methods:{updateDomData:function(){var e=this.$el.getBoundingClientRect();this.initX=e.left+tt(),this.initY=e.top+nt(),this.barWidth=this.$el.offsetWidth,this.barHeight=this.$el.offsetHeight},setValue:function(e){var n,a=e.touches?e.touches[0].pageX:e.pageX,o=e.touches?e.touches[0].pageY:e.pageY;this.orientation==="horizontal"?et(this.$el)?n=(this.initX+this.barWidth-a)*100/this.barWidth:n=(a-this.initX)*100/this.barWidth:n=(this.initY+this.barHeight-o)*100/this.barHeight;var r=(this.max-this.min)*(n/100)+this.min;if(this.step){var d=this.range?this.value[this.handleIndex]:this.value,u=r-d;u<0?r=d+Math.ceil(r/this.step-d/this.step)*this.step:u>0&&(r=d+Math.floor(r/this.step-d/this.step)*this.step)}else r=Math.floor(r);this.updateModel(e,r)},updateModel:function(e,n){var a=Math.round(n*100)/100,o;this.range?(o=this.value?Nn(this.value):[],this.handleIndex==0?(a<this.min?a=this.min:a>=this.max&&(a=this.max),o[0]=a):(a>this.max?a=this.max:a<=this.min&&(a=this.min),o[1]=a)):(a<this.min?a=this.min:a>this.max&&(a=this.max),o=a),this.writeValue(o,e),this.$emit("change",o)},onDragStart:function(e,n){this.disabled||(this.$el.setAttribute("data-p-sliding",!0),this.dragging=!0,this.updateDomData(),this.range&&this.value[0]===this.max?this.handleIndex=0:this.handleIndex=n,e.currentTarget.focus())},onDrag:function(e){this.dragging&&this.setValue(e)},onDragEnd:function(e){this.dragging&&(this.dragging=!1,this.$el.setAttribute("data-p-sliding",!1),this.$emit("slideend",{originalEvent:e,value:this.value}))},onBarClick:function(e){this.disabled||N(e.target,"data-pc-section")!=="handle"&&(this.updateDomData(),this.setValue(e))},onMouseDown:function(e,n){this.bindDragListeners(),this.onDragStart(e,n)},onKeyDown:function(e,n){switch(this.handleIndex=n,e.code){case"ArrowDown":case"ArrowLeft":this.decrementValue(e,n),e.preventDefault();break;case"ArrowUp":case"ArrowRight":this.incrementValue(e,n),e.preventDefault();break;case"PageDown":this.decrementValue(e,n,!0),e.preventDefault();break;case"PageUp":this.incrementValue(e,n,!0),e.preventDefault();break;case"Home":this.updateModel(e,this.min),e.preventDefault();break;case"End":this.updateModel(e,this.max),e.preventDefault();break}},onBlur:function(e,n){var a,o;(a=(o=this.formField).onBlur)===null||a===void 0||a.call(o,e)},decrementValue:function(e,n){var a=arguments.length>2&&arguments[2]!==void 0?arguments[2]:!1,o;this.range?this.step?o=this.value[n]-this.step:o=this.value[n]-1:this.step?o=this.value-this.step:!this.step&&a?o=this.value-10:o=this.value-1,this.updateModel(e,o),e.preventDefault()},incrementValue:function(e,n){var a=arguments.length>2&&arguments[2]!==void 0?arguments[2]:!1,o;this.range?this.step?o=this.value[n]+this.step:o=this.value[n]+1:this.step?o=this.value+this.step:!this.step&&a?o=this.value+10:o=this.value+1,this.updateModel(e,o),e.preventDefault()},bindDragListeners:function(){this.dragListener||(this.dragListener=this.onDrag.bind(this),document.addEventListener("mousemove",this.dragListener)),this.dragEndListener||(this.dragEndListener=this.onDragEnd.bind(this),document.addEventListener("mouseup",this.dragEndListener))},unbindDragListeners:function(){this.dragListener&&(document.removeEventListener("mousemove",this.dragListener),this.dragListener=null),this.dragEndListener&&(document.removeEventListener("mouseup",this.dragEndListener),this.dragEndListener=null)},rangeStyle:function(){if(this.range){var e=this.rangeEndPosition>this.rangeStartPosition?this.rangeEndPosition-this.rangeStartPosition:this.rangeStartPosition-this.rangeEndPosition,n=this.rangeEndPosition>this.rangeStartPosition?this.rangeStartPosition:this.rangeEndPosition;return this.horizontal?{"inset-inline-start":n+"%",width:e+"%"}:{bottom:n+"%",height:e+"%"}}else return this.horizontal?{width:this.handlePosition+"%"}:{height:this.handlePosition+"%"}},handleStyle:function(){return this.horizontal?{"inset-inline-start":this.handlePosition+"%"}:{bottom:this.handlePosition+"%"}},rangeStartHandleStyle:function(){return this.horizontal?{"inset-inline-start":this.rangeStartPosition+"%"}:{bottom:this.rangeStartPosition+"%"}},rangeEndHandleStyle:function(){return this.horizontal?{"inset-inline-start":this.rangeEndPosition+"%"}:{bottom:this.rangeEndPosition+"%"}}},computed:{value:function(){var e;if(this.range){var n,a,o,r;return[(n=(a=this.d_value)===null||a===void 0?void 0:a[0])!==null&&n!==void 0?n:this.min,(o=(r=this.d_value)===null||r===void 0?void 0:r[1])!==null&&o!==void 0?o:this.max]}return(e=this.d_value)!==null&&e!==void 0?e:this.min},horizontal:function(){return this.orientation==="horizontal"},vertical:function(){return this.orientation==="vertical"},handlePosition:function(){return this.value<this.min?0:this.value>this.max?100:(this.value-this.min)*100/(this.max-this.min)},rangeStartPosition:function(){return this.value&&this.value[0]!==void 0?this.value[0]<this.min?0:(this.value[0]-this.min)*100/(this.max-this.min):0},rangeEndPosition:function(){return this.value&&this.value.length===2&&this.value[1]!==void 0?this.value[1]>this.max?100:(this.value[1]-this.min)*100/(this.max-this.min):100},dataP:function(){return Q(Un({},this.orientation,this.orientation))}}},Yn=["data-p"],Qn=["data-p"],Gn=["tabindex","aria-valuemin","aria-valuenow","aria-valuemax","aria-labelledby","aria-label","aria-orientation","data-p"],Jn=["tabindex","aria-valuemin","aria-valuenow","aria-valuemax","aria-labelledby","aria-label","aria-orientation","data-p"],ea=["tabindex","aria-valuemin","aria-valuenow","aria-valuemax","aria-labelledby","aria-label","aria-orientation","data-p"];function ta(t,e,n,a,o,r){return b(),g("div",v({class:t.cx("root"),onClick:e[18]||(e[18]=function(){return r.onBarClick&&r.onBarClick.apply(r,arguments)})},t.ptmi("root"),{"data-p-sliding":!1,"data-p":r.dataP}),[i("span",v({class:t.cx("range"),style:[t.sx("range"),r.rangeStyle()]},t.ptm("range"),{"data-p":r.dataP}),null,16,Qn),t.range?x("",!0):(b(),g("span",v({key:0,class:t.cx("handle"),style:[t.sx("handle"),r.handleStyle()],onTouchstartPassive:e[0]||(e[0]=function(d){return r.onDragStart(d)}),onTouchmovePassive:e[1]||(e[1]=function(d){return r.onDrag(d)}),onTouchend:e[2]||(e[2]=function(d){return r.onDragEnd(d)}),onMousedown:e[3]||(e[3]=function(d){return r.onMouseDown(d)}),onKeydown:e[4]||(e[4]=function(d){return r.onKeyDown(d)}),onBlur:e[5]||(e[5]=function(d){return r.onBlur(d)}),tabindex:t.tabindex,role:"slider","aria-valuemin":t.min,"aria-valuenow":t.d_value,"aria-valuemax":t.max,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,"aria-orientation":t.orientation},t.ptm("handle"),{"data-p":r.dataP}),null,16,Gn)),t.range?(b(),g("span",v({key:1,class:t.cx("handle"),style:[t.sx("handle"),r.rangeStartHandleStyle()],onTouchstartPassive:e[6]||(e[6]=function(d){return r.onDragStart(d,0)}),onTouchmovePassive:e[7]||(e[7]=function(d){return r.onDrag(d)}),onTouchend:e[8]||(e[8]=function(d){return r.onDragEnd(d)}),onMousedown:e[9]||(e[9]=function(d){return r.onMouseDown(d,0)}),onKeydown:e[10]||(e[10]=function(d){return r.onKeyDown(d,0)}),onBlur:e[11]||(e[11]=function(d){return r.onBlur(d,0)}),tabindex:t.tabindex,role:"slider","aria-valuemin":t.min,"aria-valuenow":t.d_value?t.d_value[0]:null,"aria-valuemax":t.max,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,"aria-orientation":t.orientation},t.ptm("startHandler"),{"data-p":r.dataP}),null,16,Jn)):x("",!0),t.range?(b(),g("span",v({key:2,class:t.cx("handle"),style:[t.sx("handle"),r.rangeEndHandleStyle()],onTouchstartPassive:e[12]||(e[12]=function(d){return r.onDragStart(d,1)}),onTouchmovePassive:e[13]||(e[13]=function(d){return r.onDrag(d)}),onTouchend:e[14]||(e[14]=function(d){return r.onDragEnd(d)}),onMousedown:e[15]||(e[15]=function(d){return r.onMouseDown(d,1)}),onKeydown:e[16]||(e[16]=function(d){return r.onKeyDown(d,1)}),onBlur:e[17]||(e[17]=function(d){return r.onBlur(d,1)}),tabindex:t.tabindex,role:"slider","aria-valuemin":t.min,"aria-valuenow":t.d_value?t.d_value[1]:null,"aria-valuemax":t.max,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,"aria-orientation":t.orientation},t.ptm("endHandler"),{"data-p":r.dataP}),null,16,ea)):x("",!0)],16,Yn)}Ke.render=ta;const na={class:"p-4 flex flex-col gap-4"},aa={key:0,class:"flex justify-center"},la={key:1},ra={class:"flex flex-col gap-6"},ia={class:"flex flex-col gap-4"},oa={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},sa={class:"flex flex-col gap-2"},da={class:"flex flex-col gap-2"},ua={class:"flex flex-col gap-2"},ca={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},pa={class:"flex items-center gap-2"},fa=["for"],ba={class:"flex flex-col gap-2"},ga={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},va=["for"],ha={class:"flex flex-col gap-4"},ma={class:"flex flex-col gap-2"},ya={class:"flex flex-col gap-4"},wa={class:"flex items-center gap-2 p-3 bg-gray-800 rounded border border-gray-700"},xa={key:0,class:"flex flex-col gap-2"},ka={class:"flex items-center gap-2"},Pa={key:0,class:"flex flex-col gap-6 mt-4"},Sa={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},Ta={class:"flex flex-col gap-2"},Aa={class:"flex flex-col gap-2"},$a={class:"flex flex-col gap-2"},Va={class:"flex flex-col gap-2"},Ba={class:"grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 pt-4"},Ca={class:"flex flex-col gap-2"},Ia={class:"flex flex-col gap-2"},Da={class:"flex flex-col gap-3 border border-green-600/50 rounded bg-green-900/10 p-4"},La={class:"flex items-center gap-2"},Ea={key:0,class:"ml-8"},za={key:1,class:"text-gray-400 italic"},Oa={class:"flex flex-col gap-6"},_a={class:"flex items-center gap-2"},Ka={key:0,class:"flex flex-col gap-4"},ja={class:"flex flex-col gap-2"},Ha={class:"flex flex-col gap-2"},qa={class:"flex items-center gap-2"},Ua={key:0,class:"flex flex-col gap-6"},Fa={class:"flex flex-col gap-2"},Ma={key:0,class:"text-yellow-400 flex items-center gap-1"},Na={key:1,class:"text-gray-400"},Ra={class:"flex flex-col gap-2"},Wa={class:"flex items-center gap-4"},Za={class:"font-mono"},Xa={class:"flex flex-col gap-6"},Ya={class:"flex flex-col gap-4"},Qa={class:"flex flex-col gap-2"},Ga={class:"flex items-center gap-2 mt-2"},Ja={class:"flex items-center gap-2"},el={key:0,class:"flex flex-col gap-4"},tl={class:"bg-yellow-900/20 border border-yellow-600/50 p-3 rounded text-yellow-200 text-sm flex items-start gap-2"},nl={class:"grid grid-cols-1 md:grid-cols-2 gap-6"},al={class:"flex flex-col gap-2"},ll={class:"flex flex-col gap-2"},rl={class:"grid grid-cols-1 xl:grid-cols-2 gap-6"},il={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},ol={class:"flex items-center justify-between bg-gray-900/50 p-3 rounded"},sl={class:"font-mono"},dl={class:"text-right"},ul={class:"font-mono text-green-400"},cl={class:"flex items-center gap-2 mt-2"},pl={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},fl={class:"flex gap-2"},bl={class:"mt-2 max-h-40 overflow-y-auto"},gl={class:"truncate"},vl={class:"flex gap-1"},hl={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3 xl:col-span-2"},ml={class:"flex gap-4"},yl={class:"flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4 sticky bottom-0 bg-gray-900/90 backdrop-blur p-4 z-10"},wl={class:"flex flex-col gap-4"},Dl={__name:"Config",setup(t){const e=w({idm:{host:"",port:502,circuits:["A"],zones:[]},metrics:{url:""},web:{write_enabled:!1},logging:{interval:60,realtime_mode:!1},mqtt:{enabled:!1,broker:"",port:1883,username:"",topic_prefix:"idm/heatpump",qos:0,use_tls:!1,publish_interval:60,ha_discovery_enabled:!1,ha_discovery_prefix:"homeassistant"},network_security:{enabled:!1,whitelist:[],blacklist:[]},signal:{enabled:!1,cli_path:"signal-cli",sender:"",recipients:[]},ai:{enabled:!1,sensitivity:3,model:"rolling"},updates:{enabled:!1,interval_hours:12,mode:"apply",target:"all"}}),n=w([{label:"Statistisch (Rolling Window)",value:"rolling"},{label:"Isolation Forest (Expert)",value:"isolation_forest"}]),a=w(""),o=w(""),r=w(""),d=w(""),u=w(""),h=w({}),T=w({}),L=w(!1),xe=w(""),ke=w(!0),ne=w(!1),y=at(),ae=lt(),Pe=w([]),Se=w(!1),le=w(!1),Te=w(!1),q=w(null),re=w(null),je=w("http://localhost:8888"),U=w(!1),F=w(""),ie=w(!1);rt(async()=>{try{typeof window<"u"&&(je.value=`${window.location.protocol}//${window.location.hostname}:8428/vmui/`);const f=await k.get("/api/config");e.value=f.data,e.value.network_security&&(r.value=(e.value.network_security.whitelist||[]).join(`
`),d.value=(e.value.network_security.blacklist||[]).join(`
`)),e.value.signal&&(u.value=(e.value.signal.recipients||[]).join(`
`));try{const l=await k.get("/api/health");xe.value=l.data.client_ip||"Unbekannt"}catch(l){console.error("Failed to get client IP",l)}oe(),qe()}catch{y.add({severity:"error",summary:"Fehler",detail:"Konfiguration konnte nicht geladen werden",life:3e3})}finally{ke.value=!1}});const He=async()=>{try{const f=await k.post("/api/signal/test",{message:"Signal Test vom IDM Metrics Collector"});f.data.success?y.add({severity:"success",summary:"Erfolg",detail:f.data.message,life:3e3}):y.add({severity:"error",summary:"Fehler",detail:f.data.error||"Signal Test fehlgeschlagen",life:3e3})}catch(f){y.add({severity:"error",summary:"Fehler",detail:f.response?.data?.error||f.message,life:5e3})}},qe=async()=>{L.value=!0;try{const[f,l]=await Promise.all([k.get("/api/check-update"),k.get("/api/signal/status")]);h.value=f.data,T.value=l.data}catch{y.add({severity:"error",summary:"Fehler",detail:"Status konnte nicht geladen werden",life:3e3})}finally{L.value=!1}},Ue=async()=>{ne.value=!0;try{const f={idm_host:e.value.idm.host,idm_port:e.value.idm.port,circuits:e.value.idm.circuits,zones:e.value.idm.zones,metrics_url:e.value.metrics.url,write_enabled:e.value.web.write_enabled,logging_interval:e.value.logging.interval,realtime_mode:e.value.logging.realtime_mode,mqtt_enabled:e.value.mqtt?.enabled||!1,mqtt_broker:e.value.mqtt?.broker||"",mqtt_port:e.value.mqtt?.port||1883,mqtt_username:e.value.mqtt?.username||"",mqtt_password:o.value||void 0,mqtt_topic_prefix:e.value.mqtt?.topic_prefix||"idm/heatpump",mqtt_qos:e.value.mqtt?.qos||0,mqtt_use_tls:e.value.mqtt?.use_tls||!1,mqtt_publish_interval:e.value.mqtt?.publish_interval||60,mqtt_ha_discovery_enabled:e.value.mqtt?.ha_discovery_enabled||!1,mqtt_ha_discovery_prefix:e.value.mqtt?.ha_discovery_prefix||"homeassistant",network_security_enabled:e.value.network_security?.enabled||!1,network_security_whitelist:r.value,network_security_blacklist:d.value,signal_enabled:e.value.signal?.enabled||!1,signal_sender:e.value.signal?.sender||"",signal_cli_path:e.value.signal?.cli_path||"signal-cli",signal_recipients:u.value,ai_enabled:e.value.ai?.enabled||!1,ai_sensitivity:e.value.ai?.sensitivity||3,ai_model:e.value.ai?.model||"rolling",updates_enabled:e.value.updates?.enabled||!1,updates_interval_hours:e.value.updates?.interval_hours||12,updates_mode:e.value.updates?.mode||"apply",updates_target:e.value.updates?.target||"all",new_password:a.value||void 0},l=await k.post("/api/config",f);y.add({severity:"success",summary:"Erfolg",detail:l.data.message||"Einstellungen erfolgreich gespeichert",life:3e3}),a.value="",o.value=""}catch(f){y.add({severity:"error",summary:"Fehler",detail:f.response?.data?.error||f.message,life:5e3})}finally{ne.value=!1}},Fe=()=>{ae.require({message:"Bist du sicher, dass du den Dienst neu starten möchtest?",header:"Bestätigung",icon:"pi pi-exclamation-triangle",accept:async()=>{try{const f=await k.post("/api/restart");y.add({severity:"info",summary:"Neustart",detail:f.data.message,life:3e3})}catch{y.add({severity:"error",summary:"Fehler",detail:"Neustart fehlgeschlagen",life:3e3})}}})},oe=async()=>{Se.value=!0;try{const f=await k.get("/api/backup/list");Pe.value=f.data.backups||[]}catch{y.add({severity:"error",summary:"Fehler",detail:"Backups konnten nicht geladen werden",life:3e3})}finally{Se.value=!1}},Me=async()=>{le.value=!0;try{const f=await k.post("/api/backup/create");f.data.success?(y.add({severity:"success",summary:"Erfolg",detail:`Backup erstellt: ${f.data.filename}`,life:3e3}),oe()):y.add({severity:"error",summary:"Fehler",detail:f.data.error,life:3e3})}catch(f){y.add({severity:"error",summary:"Fehler",detail:f.response?.data?.error||"Backup Erstellung fehlgeschlagen",life:3e3})}finally{le.value=!1}},Ne=async f=>{try{const l=await k.get(`/api/backup/download/${f}`,{responseType:"blob"}),s=window.URL.createObjectURL(new Blob([l.data])),A=document.createElement("a");A.href=s,A.setAttribute("download",f),document.body.appendChild(A),A.click(),A.remove(),y.add({severity:"success",summary:"Erfolg",detail:"Backup heruntergeladen",life:2e3})}catch{y.add({severity:"error",summary:"Fehler",detail:"Backup Download fehlgeschlagen",life:3e3})}},Re=f=>{ae.require({message:`Backup "${f}" löschen?`,header:"Backup Löschen",icon:"pi pi-trash",acceptClass:"p-button-danger",accept:async()=>{try{await k.delete(`/api/backup/delete/${f}`),y.add({severity:"success",summary:"Erfolg",detail:"Backup gelöscht",life:2e3}),oe()}catch{y.add({severity:"error",summary:"Fehler",detail:"Backup löschen fehlgeschlagen",life:3e3})}}})},We=f=>{const l=f.target.files[0];q.value=l},Ze=async()=>{q.value&&ae.require({message:"Konfiguration aus hochgeladener Datei wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!",header:"Aus Datei Wiederherstellen",icon:"pi pi-exclamation-triangle",acceptClass:"p-button-warning",accept:async()=>{Te.value=!0;try{const f=new FormData;f.append("file",q.value),f.append("restore_secrets","false");const l=await k.post("/api/backup/restore",f,{headers:{"Content-Type":"multipart/form-data"}});l.data.success?(y.add({severity:"success",summary:"Erfolg",detail:l.data.message,life:5e3}),q.value=null,re.value&&(re.value.value=""),setTimeout(()=>location.reload(),2e3)):y.add({severity:"error",summary:"Fehler",detail:l.data.error,life:5e3})}catch(f){y.add({severity:"error",summary:"Fehler",detail:f.response?.data?.error||"Wiederherstellung fehlgeschlagen",life:5e3})}finally{Te.value=!1}}})},Xe=async()=>{if(F.value==="DELETE"){ie.value=!0;try{const f=await k.post("/api/database/delete");f.data.success?(y.add({severity:"success",summary:"Erfolg",detail:f.data.message,life:5e3}),U.value=!1,F.value=""):y.add({severity:"error",summary:"Fehler",detail:f.data.error,life:5e3})}catch(f){y.add({severity:"error",summary:"Fehler",detail:f.response?.data?.error||"Datenbank löschen fehlgeschlagen",life:5e3})}finally{ie.value=!1}}};return(f,l)=>(b(),g("div",na,[l[77]||(l[77]=i("h1",{class:"text-2xl font-bold mb-4"},"Konfiguration",-1)),ke.value?(b(),g("div",aa,[...l[34]||(l[34]=[i("i",{class:"pi pi-spin pi-spinner text-4xl"},null,-1)])])):(b(),g("div",la,[c(p(ze),null,{default:m(()=>[c(p(_),{header:"Verbindung"},{default:m(()=>[i("div",ra,[c(p(I),{legend:"IDM Wärmepumpe",toggleable:!0},{default:m(()=>[i("div",ia,[i("div",oa,[i("div",sa,[l[35]||(l[35]=i("label",null,"Host / IP",-1)),c(p(C),{modelValue:e.value.idm.host,"onUpdate:modelValue":l[0]||(l[0]=s=>e.value.idm.host=s),class:"w-full"},null,8,["modelValue"])]),i("div",da,[l[36]||(l[36]=i("label",null,"Port",-1)),c(p(se),{modelValue:e.value.idm.port,"onUpdate:modelValue":l[1]||(l[1]=s=>e.value.idm.port=s),useGrouping:!1,class:"w-full"},null,8,["modelValue"])])]),i("div",ua,[l[38]||(l[38]=i("label",{class:"font-bold"},"Aktivierte Heizkreise",-1)),i("div",ca,[i("div",pa,[c(p($),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":l[2]||(l[2]=s=>e.value.idm.circuits=s),inputId:"circuitA",value:"A",disabled:""},null,8,["modelValue"]),l[37]||(l[37]=i("label",{for:"circuitA",class:"opacity-50"},"Heizkreis A (Fest)",-1))]),(b(),g(D,null,H(["B","C","D","E","F","G"],s=>i("div",{key:s,class:"flex items-center gap-2"},[c(p($),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":l[3]||(l[3]=A=>e.value.idm.circuits=A),inputId:"circuit"+s,value:s},null,8,["modelValue","inputId","value"]),i("label",{for:"circuit"+s},"Heizkreis "+S(s),9,fa)])),64))])]),i("div",ba,[l[39]||(l[39]=i("label",{class:"font-bold"},"Zonenmodule",-1)),i("div",ga,[(b(),g(D,null,H(10,s=>i("div",{key:s,class:"flex items-center gap-2"},[c(p($),{modelValue:e.value.idm.zones,"onUpdate:modelValue":l[4]||(l[4]=A=>e.value.idm.zones=A),inputId:"zone"+(s-1),value:s-1},null,8,["modelValue","inputId","value"]),i("label",{for:"zone"+(s-1)},"Zone "+S(s),9,va)])),64))])])])]),_:1}),c(p(I),{legend:"Datenbank (VictoriaMetrics)",toggleable:!0},{default:m(()=>[i("div",ha,[i("div",ma,[l[40]||(l[40]=i("label",null,"Write URL",-1)),c(p(C),{modelValue:e.value.metrics.url,"onUpdate:modelValue":l[5]||(l[5]=s=>e.value.metrics.url=s),class:"w-full"},null,8,["modelValue"]),l[41]||(l[41]=i("small",{class:"text-gray-300"},"Standard: http://victoriametrics:8428/write",-1))])])]),_:1}),c(p(I),{legend:"Datenerfassung",toggleable:!0},{default:m(()=>[i("div",ya,[i("div",wa,[c(p($),{modelValue:e.value.logging.realtime_mode,"onUpdate:modelValue":l[6]||(l[6]=s=>e.value.logging.realtime_mode=s),binary:"",inputId:"realtime_mode"},null,8,["modelValue"]),l[42]||(l[42]=i("div",{class:"flex flex-col"},[i("label",{for:"realtime_mode",class:"font-bold cursor-pointer"},"Echtzeit-Modus"),i("span",{class:"text-sm text-gray-400"},"Aktualisierung im Sekundentakt (Hohe Last)")],-1))]),e.value.logging.realtime_mode?x("",!0):(b(),g("div",xa,[l[43]||(l[43]=i("label",null,"Abfrage-Intervall (Sekunden)",-1)),c(p(se),{modelValue:e.value.logging.interval,"onUpdate:modelValue":l[7]||(l[7]=s=>e.value.logging.interval=s),min:1,max:3600,useGrouping:!1,class:"w-full md:w-1/2"},null,8,["modelValue"]),l[44]||(l[44]=i("small",{class:"text-gray-400"},"Standard: 60 Sekunden",-1))]))])]),_:1})])]),_:1}),c(p(_),{header:"MQTT & Integration"},{default:m(()=>[c(p(I),{legend:"MQTT Publishing",toggleable:!1},{legend:m(()=>[i("div",ka,[c(p($),{modelValue:e.value.mqtt.enabled,"onUpdate:modelValue":l[8]||(l[8]=s=>e.value.mqtt.enabled=s),binary:"",inputId:"mqtt_enabled"},null,8,["modelValue"]),l[45]||(l[45]=i("span",{class:"font-bold text-lg"},"MQTT Aktivieren",-1))])]),default:m(()=>[e.value.mqtt.enabled?(b(),g("div",Pa,[i("div",Sa,[i("div",Ta,[l[46]||(l[46]=i("label",null,"Broker Adresse",-1)),c(p(C),{modelValue:e.value.mqtt.broker,"onUpdate:modelValue":l[9]||(l[9]=s=>e.value.mqtt.broker=s),placeholder:"mqtt.example.com",class:"w-full"},null,8,["modelValue"])]),i("div",Aa,[l[47]||(l[47]=i("label",null,"Port",-1)),c(p(se),{modelValue:e.value.mqtt.port,"onUpdate:modelValue":l[10]||(l[10]=s=>e.value.mqtt.port=s),useGrouping:!1,min:1,max:65535,class:"w-full"},null,8,["modelValue"])]),i("div",$a,[l[48]||(l[48]=i("label",null,"Benutzername",-1)),c(p(C),{modelValue:e.value.mqtt.username,"onUpdate:modelValue":l[11]||(l[11]=s=>e.value.mqtt.username=s),placeholder:"Optional",class:"w-full"},null,8,["modelValue"])]),i("div",Va,[l[49]||(l[49]=i("label",null,"Passwort",-1)),c(p(C),{modelValue:o.value,"onUpdate:modelValue":l[12]||(l[12]=s=>o.value=s),type:"password",placeholder:"••••••",class:"w-full"},null,8,["modelValue"])])]),i("div",Ba,[i("div",Ca,[l[50]||(l[50]=i("label",null,"Topic Präfix",-1)),c(p(C),{modelValue:e.value.mqtt.topic_prefix,"onUpdate:modelValue":l[13]||(l[13]=s=>e.value.mqtt.topic_prefix=s),class:"w-full"},null,8,["modelValue"])]),i("div",Ia,[l[51]||(l[51]=i("label",null,"QoS Level",-1)),c(p(fe),{modelValue:e.value.mqtt.qos,"onUpdate:modelValue":l[14]||(l[14]=s=>e.value.mqtt.qos=s),options:[0,1,2],"aria-labelledby":"basic",class:"w-full"},null,8,["modelValue"])])]),i("div",Da,[i("div",La,[c(p($),{modelValue:e.value.mqtt.ha_discovery_enabled,"onUpdate:modelValue":l[15]||(l[15]=s=>e.value.mqtt.ha_discovery_enabled=s),binary:"",inputId:"ha_discovery"},null,8,["modelValue"]),l[52]||(l[52]=i("label",{for:"ha_discovery",class:"font-bold text-green-400 cursor-pointer"},"Home Assistant Auto-Discovery",-1))]),e.value.mqtt.ha_discovery_enabled?(b(),g("div",Ea,[l[53]||(l[53]=i("label",{class:"text-sm"},"Discovery Präfix",-1)),c(p(C),{modelValue:e.value.mqtt.ha_discovery_prefix,"onUpdate:modelValue":l[16]||(l[16]=s=>e.value.mqtt.ha_discovery_prefix=s),class:"w-full mt-1"},null,8,["modelValue"])])):x("",!0)])])):(b(),g("div",za," Aktivieren Sie MQTT, um Daten an Broker wie Mosquitto oder Home Assistant zu senden. "))]),_:1})]),_:1}),c(p(_),{header:"Benachrichtigungen"},{default:m(()=>[i("div",Oa,[c(p(I),{legend:"Signal Messenger",toggleable:!0},{legend:m(()=>[i("div",_a,[c(p($),{modelValue:e.value.signal.enabled,"onUpdate:modelValue":l[17]||(l[17]=s=>e.value.signal.enabled=s),binary:""},null,8,["modelValue"]),l[54]||(l[54]=i("span",{class:"font-bold"},"Signal",-1))])]),default:m(()=>[e.value.signal.enabled?(b(),g("div",Ka,[i("div",ja,[l[55]||(l[55]=i("label",null,"Sender Nummer",-1)),c(p(C),{modelValue:e.value.signal.sender,"onUpdate:modelValue":l[18]||(l[18]=s=>e.value.signal.sender=s),placeholder:"+49...",class:"w-full md:w-1/2"},null,8,["modelValue"])]),i("div",Ha,[l[56]||(l[56]=i("label",null,"Empfänger (Pro Zeile eine Nummer)",-1)),c(p(ee),{modelValue:u.value,"onUpdate:modelValue":l[19]||(l[19]=s=>u.value=s),rows:"3",class:"w-full font-mono"},null,8,["modelValue"])]),c(p(V),{label:"Testnachricht senden",icon:"pi pi-send",severity:"success",outlined:"",onClick:He,class:"w-full md:w-auto self-start"})])):x("",!0)]),_:1}),c(p(I),{legend:"KI & Anomalieerkennung",toggleable:!0},{legend:m(()=>[i("div",qa,[c(p($),{modelValue:e.value.ai.enabled,"onUpdate:modelValue":l[20]||(l[20]=s=>e.value.ai.enabled=s),binary:""},null,8,["modelValue"]),l[57]||(l[57]=i("span",{class:"font-bold"},"KI-Analyse aktivieren",-1))])]),default:m(()=>[e.value.ai.enabled?(b(),g("div",Ua,[i("div",Fa,[l[59]||(l[59]=i("label",{class:"font-bold"},"Modell-Typ",-1)),c(p(fe),{modelValue:e.value.ai.model,"onUpdate:modelValue":l[21]||(l[21]=s=>e.value.ai.model=s),options:n.value,optionLabel:"label",optionValue:"value","aria-labelledby":"basic",class:"w-full md:w-1/2"},null,8,["modelValue","options"]),e.value.ai.model==="isolation_forest"?(b(),g("small",Ma,[...l[58]||(l[58]=[i("i",{class:"pi pi-exclamation-triangle"},null,-1),E(' Achtung: "Isolation Forest" benötigt viel RAM/CPU. Nicht für Raspberry Pi Zero/3 empfohlen! ',-1)])])):(b(),g("small",Na," Standard: Gleitendes Fenster für flexible Anpassung an Jahreszeiten. "))]),i("div",Ra,[l[60]||(l[60]=i("label",null,"Sensitivität (Sigma)",-1)),i("div",Wa,[c(p(Ke),{modelValue:e.value.ai.sensitivity,"onUpdate:modelValue":l[22]||(l[22]=s=>e.value.ai.sensitivity=s),min:1,max:10,step:.1,class:"w-full md:w-1/2"},null,8,["modelValue"]),i("span",Za,S(e.value.ai.sensitivity)+" σ",1)]),l[61]||(l[61]=i("small",{class:"text-gray-400"},"Höherer Wert = Weniger Alarme (nur extreme Abweichungen).",-1))])])):x("",!0)]),_:1})])]),_:1}),c(p(_),{header:"Sicherheit"},{default:m(()=>[i("div",Xa,[c(p(I),{legend:"Webzugriff",toggleable:!0},{default:m(()=>[i("div",Ya,[i("div",Qa,[l[62]||(l[62]=i("label",null,"Admin Passwort ändern",-1)),c(p(C),{modelValue:a.value,"onUpdate:modelValue":l[23]||(l[23]=s=>a.value=s),type:"password",placeholder:"Neues Passwort eingeben...",class:"w-full md:w-1/2"},null,8,["modelValue"])]),i("div",Ga,[c(p($),{modelValue:e.value.web.write_enabled,"onUpdate:modelValue":l[24]||(l[24]=s=>e.value.web.write_enabled=s),binary:"",inputId:"write_access"},null,8,["modelValue"]),l[63]||(l[63]=i("div",{class:"flex flex-col"},[i("label",{for:"write_access",class:"font-bold cursor-pointer"},"Schreibzugriff erlauben"),i("span",{class:"text-sm text-gray-400"},"Erforderlich für manuelle Steuerung und Zeitpläne")],-1))])])]),_:1}),c(p(I),{legend:"Netzwerk Firewall",toggleable:!0},{legend:m(()=>[i("div",Ja,[c(p($),{modelValue:e.value.network_security.enabled,"onUpdate:modelValue":l[25]||(l[25]=s=>e.value.network_security.enabled=s),binary:""},null,8,["modelValue"]),l[64]||(l[64]=i("span",{class:"font-bold"},"IP Whitelist/Blacklist",-1))])]),default:m(()=>[e.value.network_security.enabled?(b(),g("div",el,[i("div",tl,[l[67]||(l[67]=i("i",{class:"pi pi-exclamation-triangle mt-0.5"},null,-1)),i("span",null,[l[65]||(l[65]=E("Deine IP ist ",-1)),i("strong",null,S(xe.value),1),l[66]||(l[66]=E(". Füge diese zur Whitelist hinzu, sonst sperrst du dich aus!",-1))])]),i("div",nl,[i("div",al,[l[68]||(l[68]=i("label",{class:"font-bold text-green-400"},"Whitelist (Erlaubt)",-1)),c(p(ee),{modelValue:r.value,"onUpdate:modelValue":l[26]||(l[26]=s=>r.value=s),rows:"5",class:"w-full font-mono text-sm",placeholder:"192.168.1.0/24"},null,8,["modelValue"])]),i("div",ll,[l[69]||(l[69]=i("label",{class:"font-bold text-red-400"},"Blacklist (Blockiert)",-1)),c(p(ee),{modelValue:d.value,"onUpdate:modelValue":l[27]||(l[27]=s=>d.value=s),rows:"5",class:"w-full font-mono text-sm",placeholder:"1.2.3.4"},null,8,["modelValue"])])])])):x("",!0)]),_:1})])]),_:1}),c(p(_),{header:"System & Wartung"},{default:m(()=>[i("div",rl,[i("div",il,[l[73]||(l[73]=i("h3",{class:"font-bold text-lg flex items-center gap-2"},[i("i",{class:"pi pi-refresh"}),E(" Update Status ")],-1)),i("div",ol,[i("div",null,[l[70]||(l[70]=i("div",{class:"text-sm text-gray-400"},"Installierte Version",-1)),i("div",sl,S(h.value.current_version||"v0.0.0"),1)]),i("div",dl,[l[71]||(l[71]=i("div",{class:"text-sm text-gray-400"},"Verfügbare Version",-1)),i("div",ul,S(h.value.latest_version||"Checking..."),1)])]),i("div",cl,[c(p($),{modelValue:e.value.updates.enabled,"onUpdate:modelValue":l[28]||(l[28]=s=>e.value.updates.enabled=s),binary:"",inputId:"auto_updates"},null,8,["modelValue"]),l[72]||(l[72]=i("label",{for:"auto_updates"},"Auto-Updates aktivieren",-1))])]),i("div",pl,[l[74]||(l[74]=i("h3",{class:"font-bold text-lg flex items-center gap-2"},[i("i",{class:"pi pi-database"}),E(" Backup ")],-1)),i("div",fl,[c(p(V),{label:"Backup erstellen",icon:"pi pi-download",size:"small",onClick:Me,loading:le.value},null,8,["loading"]),c(p(V),{label:"Backup hochladen",icon:"pi pi-upload",size:"small",severity:"secondary",onClick:l[29]||(l[29]=s=>f.$refs.fileInput.click())}),i("input",{type:"file",ref_key:"fileInput",ref:re,class:"hidden",onChange:We,accept:".zip"},null,544)]),q.value?(b(),O(p(V),{key:0,label:"Wiederherstellen starten",severity:"warning",class:"w-full mt-2",onClick:Ze})):x("",!0),i("div",bl,[(b(!0),g(D,null,H(Pe.value,s=>(b(),g("div",{key:s.filename,class:"flex justify-between items-center p-2 hover:bg-gray-700 rounded text-sm border-b border-gray-700 last:border-0"},[i("span",gl,S(s.filename),1),i("div",vl,[c(p(V),{icon:"pi pi-download",text:"",size:"small",onClick:A=>Ne(s.filename)},null,8,["onClick"]),c(p(V),{icon:"pi pi-trash",text:"",severity:"danger",size:"small",onClick:A=>Re(s.filename)},null,8,["onClick"])])]))),128))])]),i("div",hl,[l[75]||(l[75]=i("h3",{class:"font-bold text-lg flex items-center gap-2 text-red-400"},[i("i",{class:"pi pi-power-off"}),E(" Danger Zone ")],-1)),i("div",ml,[c(p(V),{label:"Dienst neu starten",icon:"pi pi-refresh",severity:"warning",onClick:Fe}),c(p(V),{label:"Datenbank löschen",icon:"pi pi-trash",severity:"danger",onClick:l[30]||(l[30]=s=>U.value=!0)})])])])]),_:1}),c(p(_),{header:"Tools"},{default:m(()=>[c(ct)]),_:1})]),_:1})])),i("div",yl,[c(p(V),{label:"Speichern",icon:"pi pi-save",onClick:Ue,loading:ne.value,size:"large",severity:"primary"},null,8,["loading"])]),c(p(ut),{visible:U.value,"onUpdate:visible":l[33]||(l[33]=s=>U.value=s),modal:"",header:"Datenbank löschen",style:{width:"450px"}},{footer:m(()=>[c(p(V),{label:"Abbrechen",text:"",onClick:l[32]||(l[32]=s=>U.value=!1)}),c(p(V),{label:"Alles löschen",severity:"danger",onClick:Xe,disabled:F.value!=="DELETE",loading:ie.value},null,8,["disabled","loading"])]),default:m(()=>[i("div",wl,[l[76]||(l[76]=i("div",{class:"flex items-start gap-3"},[i("i",{class:"pi pi-exclamation-triangle text-red-500 text-2xl"}),i("div",{class:"flex flex-col gap-2"},[i("span",{class:"font-bold text-lg"},"Bist du dir absolut sicher?"),i("p",{class:"text-gray-300"},[E(" Diese Aktion löscht "),i("span",{class:"font-bold text-red-400"},"ALLE"),E(" Daten dauerhaft aus der Datenbank. ")])])],-1)),c(p(C),{modelValue:F.value,"onUpdate:modelValue":l[31]||(l[31]=s=>F.value=s),placeholder:"Tippe DELETE",class:"w-full"},null,8,["modelValue"])])]),_:1},8,["visible"]),c(p(st)),c(p(dt))]))}};export{Dl as default};
