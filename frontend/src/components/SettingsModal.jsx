import { useState, useEffect } from 'react';
import './SettingsModal.css';

export default function SettingsModal({ isOpen, onClose, settings, onSave }) {
    const [apiKey, setApiKey] = useState('');
    const [councilModels, setCouncilModels] = useState([]);
    const [chairmanModel, setChairmanModel] = useState('');
    const [organizationName, setOrganizationName] = useState('');
    const [availableModels, setAvailableModels] = useState([]);

    useEffect(() => {
        if (settings && isOpen) {
            setApiKey(settings.openrouter_api_key || '');
            setCouncilModels(settings.council_models || []);
            setChairmanModel(settings.chairman_model || '');
            setOrganizationName(settings.organization_name || '');
            setAvailableModels(settings.available_models || []);
        }
    }, [settings, isOpen]);

    if (!isOpen) return null;

    const handleSave = () => {
        onSave({
            openrouter_api_key: apiKey,
            council_models: councilModels,
            chairman_model: chairmanModel,
            organization_name: organizationName,
        });
        onClose();
    };

    const toggleCouncilModel = (model) => {
        if (councilModels.includes(model)) {
            setCouncilModels(councilModels.filter((m) => m !== model));
        } else {
            setCouncilModels([...councilModels, model]);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Settings</h2>
                    <button className="close-btn" onClick={onClose}>
                        ×
                    </button>
                </div>

                <div className="modal-body">
                    <div className="form-group">
                        <label>Organization Name</label>
                        <input
                            type="text"
                            value={organizationName}
                            onChange={(e) => setOrganizationName(e.target.value)}
                            placeholder="e.g. 守谷市"
                        />
                        <p className="help-text">
                            The name of the organization (displayed in the title).
                        </p>
                    </div>

                    <div className="form-group">
                        <label>OpenRouter API Key</label>
                        <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder="sk-or-v1-..."
                        />
                        <p className="help-text">
                            Required for accessing LLMs via OpenRouter.
                        </p>
                    </div>

                    <div className="form-group">
                        <label>Council Models</label>
                        <div className="checkbox-list">
                            {availableModels.map((model) => (
                                <div key={model} className="checkbox-item">
                                    <input
                                        type="checkbox"
                                        id={`council-${model}`}
                                        checked={councilModels.includes(model)}
                                        onChange={() => toggleCouncilModel(model)}
                                    />
                                    <label htmlFor={`council-${model}`}>{model}</label>
                                </div>
                            ))}
                        </div>
                        <p className="help-text">
                            Select models to participate in the council (Stage 1 & 2).
                        </p>
                    </div>

                    <div className="form-group">
                        <label>Chairman Model</label>
                        <select
                            value={chairmanModel}
                            onChange={(e) => setChairmanModel(e.target.value)}
                        >
                            {availableModels.map((model) => (
                                <option key={model} value={model}>
                                    {model}
                                </option>
                            ))}
                        </select>
                        <p className="help-text">
                            Select the model to synthesize the final response (Stage 3).
                        </p>
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="cancel-btn" onClick={onClose}>
                        Cancel
                    </button>
                    <button className="save-btn" onClick={handleSave}>
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
}
