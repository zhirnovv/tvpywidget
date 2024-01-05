// Copyright (c) Vasya Zhirnov
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

declare global {
  interface Window {
    Plotly: any;
  }
}

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/widget.css';

// Import side packages
import 'glow';
import 'jquery-ui.custom';
import Plotly from 'plotly-dist';

export class ExampleModel extends DOMWidgetModel {
  defaults(): any {
    return {
      ...super.defaults(),
      _model_name: ExampleModel.model_name,
      _model_module: ExampleModel.model_module,
      _model_module_version: ExampleModel.model_module_version,
      _view_name: ExampleModel.view_name,
      _view_module: ExampleModel.view_module,
      _view_module_version: ExampleModel.view_module_version,
      value: 'Hello World',
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'ExampleModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'ExampleView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class ExampleView extends DOMWidgetView {
  render(): void {
    this.el.classList.add('custom-widget');
    this.el.id = btoa('sexy');

    this.value_changed();
    this.model.on('change:value', this.value_changed, this);

    window.Plotly = Plotly;
    console.log('loaded plotly');
  }

  value_changed(): void {
    const canvas = document.createElement('canvas');
    canvas.classList.add('sexy');

    canvas.style.height = '200px';
    canvas.style.width = '200px';
    canvas.style.background = 'black';
    const ctx = canvas.getContext('2d');
    console.log(ctx);
    if (ctx) {
      ctx.font = '30px Comic Sans';
      ctx.fillStyle = 'white';
      ctx.fillText(this.model.get('value'), 10, 50);
    }

    this.el.appendChild(canvas);
  }
}
