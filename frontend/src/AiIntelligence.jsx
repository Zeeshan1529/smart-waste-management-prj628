import React, { useState } from 'react';

const API = 'http://127.0.0.1:8000';

function AiIntelligence() {
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [predictionError, setPredictionError] = useState('');

  const [form, setForm] = useState({
    ward: 'Ward 18',
    day_of_week: 3,
    month: 8,
    fill_level: 70,
    capacity_kg: 100,
    previous_day_kg: 95,
    avg_3_day_kg: 92,
    avg_7_day_kg: 90,
  });

  const [image, setImage] = useState(null);
  const [classification, setClassification] = useState(null);
  const [classifying, setClassifying] = useState(false);
  const [classificationError, setClassificationError] = useState('');

  function updateField(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function runPrediction(event) {
    event.preventDefault();

    const token = localStorage.getItem('access_token');

    if (!token) {
      setPredictionError('Authentication token not found.');
      return;
    }

    setPredicting(true);
    setPredictionError('');
    setPrediction(null);

    try {
      const response = await fetch(`${API}/api/ml/predict`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ward: form.ward,
          day_of_week: Number(form.day_of_week),
          month: Number(form.month),
          fill_level: Number(form.fill_level),
          capacity_kg: Number(form.capacity_kg),
          previous_day_kg: Number(form.previous_day_kg),
          avg_3_day_kg: Number(form.avg_3_day_kg),
          avg_7_day_kg: Number(form.avg_7_day_kg),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Prediction failed');
      }

      setPrediction(data);
    } catch (error) {
      setPredictionError(error.message);
    } finally {
      setPredicting(false);
    }
  }

  async function classifyImage(event) {
    event.preventDefault();

    if (!image) {
      setClassificationError('Choose a waste image first.');
      return;
    }

    const token = localStorage.getItem('access_token');

    if (!token) {
      setClassificationError('Authentication token not found.');
      return;
    }

    setClassifying(true);
    setClassificationError('');
    setClassification(null);

    try {
      const formData = new FormData();
      formData.append('file', image);

      const response = await fetch(`${API}/api/ml/classify-image`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Image classification failed');
      }

      setClassification(data);
    } catch (error) {
      setClassificationError(error.message);
    } finally {
      setClassifying(false);
    }
  }

  const predictionValue =
    prediction?.prediction ??
    prediction?.predicted_waste_kg ??
    prediction?.predicted_kg ??
    prediction?.waste_generation_kg ??
    null;

  const predictedClass =
    classification?.predicted_class ??
    classification?.class_name ??
    classification?.class ??
    classification?.prediction ??
    'UNKNOWN';

  const confidence =
    classification?.confidence != null
      ? Number(classification.confidence)
      : null;

  const confidencePercent =
    confidence != null
      ? `${(confidence * 100).toFixed(1)}%`
      : '--';

  const topPredictions =
    classification?.top_3 ??
    classification?.top_predictions ??
    classification?.top3 ??
    [];

  const needsReview =
    classification?.needs_review ??
    (confidence != null && confidence < 0.7);

  return (
    <section className="ai-page">
      <div className="module-hero">
        <div>
          <span className="eyebrow">AI INTELLIGENCE / DECISION ENGINE</span>

          <h1>
            Artificial Intelligence
            <span>for Waste Operations</span>
          </h1>

          <p>
            Turn historical waste patterns and visual waste signals into
            operational decisions for collection and recovery.
          </p>
        </div>

        <div className="ai-engine-status">
          <span className="status-dot"></span>
          <div>
            <strong>AI ENGINE ONLINE</strong>
            <span>ML + DL SERVICES AVAILABLE</span>
          </div>
        </div>
      </div>

      <div className="ai-grid">
        <section className="ai-card">
          <div className="ai-card-header">
            <div>
              <span className="eyebrow">MODEL 01 / MACHINE LEARNING</span>
              <h2>Waste Generation Forecast</h2>
            </div>

            <div className="model-chip">RANDOM FOREST</div>
          </div>

          <p className="ai-card-description">
            Estimate expected waste generation from ward, temporal and recent
            collection patterns.
          </p>

          <form className="prediction-form" onSubmit={runPrediction}>
            <div className="form-grid">
              <label>
                WARD
                <input
                  value={form.ward}
                  onChange={(e) => updateField('ward', e.target.value)}
                />
              </label>

              <label>
                DAY OF WEEK
                <input
                  type="number"
                  min="0"
                  max="6"
                  value={form.day_of_week}
                  onChange={(e) =>
                    updateField('day_of_week', e.target.value)
                  }
                />
              </label>

              <label>
                MONTH
                <input
                  type="number"
                  min="1"
                  max="12"
                  value={form.month}
                  onChange={(e) => updateField('month', e.target.value)}
                />
              </label>

              <label>
                CURRENT FILL %
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={form.fill_level}
                  onChange={(e) =>
                    updateField('fill_level', e.target.value)
                  }
                />
              </label>

              <label>
                CAPACITY KG
                <input
                  type="number"
                  min="1"
                  value={form.capacity_kg}
                  onChange={(e) =>
                    updateField('capacity_kg', e.target.value)
                  }
                />
              </label>

              <label>
                PREVIOUS DAY KG
                <input
                  type="number"
                  min="0"
                  value={form.previous_day_kg}
                  onChange={(e) =>
                    updateField('previous_day_kg', e.target.value)
                  }
                />
              </label>

              <label>
                3-DAY AVERAGE KG
                <input
                  type="number"
                  min="0"
                  value={form.avg_3_day_kg}
                  onChange={(e) =>
                    updateField('avg_3_day_kg', e.target.value)
                  }
                />
              </label>

              <label>
                7-DAY AVERAGE KG
                <input
                  type="number"
                  min="0"
                  value={form.avg_7_day_kg}
                  onChange={(e) =>
                    updateField('avg_7_day_kg', e.target.value)
                  }
                />
              </label>
            </div>

            {predictionError && (
              <div className="ai-error">{predictionError}</div>
            )}

            <button
              className="ai-action"
              type="submit"
              disabled={predicting}
            >
              {predicting ? 'RUNNING MODEL...' : 'RUN WASTE FORECAST →'}
            </button>
          </form>

          {predictionValue != null && (
            <div className="prediction-result">
              <span className="eyebrow">MODEL OUTPUT</span>

              <div className="prediction-number">
                {Number(predictionValue).toFixed(2)}
                <small>KG</small>
              </div>

              <div className="prediction-context">
                <span>EXPECTED WASTE GENERATION</span>
                <strong>{form.ward}</strong>
              </div>

              <div className="prediction-bar">
                <div
                  style={{
                    width: `${Math.min(
                      100,
                      (Number(predictionValue) / Number(form.capacity_kg)) * 100
                    )}%`,
                  }}
                ></div>
              </div>

              <span className="prediction-note">
                Forecast generated by the trained PRJ_628 ML model.
              </span>
            </div>
          )}
        </section>

        <section className="ai-card vision-card">
          <div className="ai-card-header">
            <div>
              <span className="eyebrow">MODEL 02 / DEEP LEARNING</span>
              <h2>Waste Vision</h2>
            </div>

            <div className="model-chip">RESNET-18</div>
          </div>

          <p className="ai-card-description">
            Classify waste images into recyclable material categories and flag
            uncertain predictions for human review.
          </p>

          <form className="vision-form" onSubmit={classifyImage}>
            <label className="upload-zone">
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setImage(e.target.files?.[0] || null)}
              />

              <span className="upload-icon">↑</span>

              <strong>
                {image ? image.name : 'DROP WASTE IMAGE HERE'}
              </strong>

              <small>
                JPG, PNG or WEBP • AI classification with confidence scoring
              </small>
            </label>

            {classificationError && (
              <div className="ai-error">{classificationError}</div>
            )}

            <button
              className="ai-action"
              type="submit"
              disabled={classifying}
            >
              {classifying ? 'ANALYZING IMAGE...' : 'CLASSIFY WASTE →'}
            </button>
          </form>

          {classification && (
            <div className="vision-result">
              <div className="classification-main">
                <div>
                  <span className="eyebrow">PREDICTED CLASS</span>

                  <h3>{String(predictedClass).toUpperCase()}</h3>
                </div>

                <div className="confidence">
                  <span>CONFIDENCE</span>
                  <strong>{confidencePercent}</strong>
                </div>
              </div>

              <div className="confidence-track">
                <div
                  style={{
                    width: confidence != null
                      ? `${Math.min(100, confidence * 100)}%`
                      : '0%',
                  }}
                ></div>
              </div>

              <div className="recovery-box">
                <span>RECOVERY STREAM</span>
                <strong>
                  {classification.recovery_stream ||
                    classification.recovery_category ||
                    'REVIEW CLASSIFICATION'}
                </strong>
              </div>

              {needsReview && (
                <div className="review-warning">
                  <strong>⚠ HUMAN REVIEW RECOMMENDED</strong>
                  <span>
                    Low-confidence predictions should be verified before
                    routing material into recovery.
                  </span>
                </div>
              )}

              {topPredictions.length > 0 && (
                <div className="top-predictions">
                  <span className="eyebrow">TOP PREDICTIONS</span>

                  {topPredictions.slice(0, 3).map((item, index) => {
                    const name =
                      item.class ??
                      item.label ??
                      item.name ??
                      `CLASS ${index + 1}`;

                    const score =
                      item.confidence ??
                      item.probability ??
                      item.score ??
                      0;

                    return (
                      <div className="top-prediction" key={`${name}-${index}`}>
                        <span>{String(name).toUpperCase()}</span>

                        <div className="mini-track">
                          <div
                            style={{
                              width: `${Math.min(100, Number(score) * 100)}%`,
                            }}
                          ></div>
                        </div>

                        <strong>
                          {(Number(score) * 100).toFixed(1)}%
                        </strong>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </section>
      </div>

      <section className="ai-flow">
        <div className="flow-intro">
          <span className="eyebrow">DECISION PIPELINE</span>
          <h2>From data to action</h2>
        </div>

        <div className="flow-step">
          <span>01</span>
          <strong>DATA</strong>
          <small>Bins + historical signals</small>
        </div>

        <div className="flow-arrow">→</div>

        <div className="flow-step">
          <span>02</span>
          <strong>PREDICT</strong>
          <small>ML waste forecast</small>
        </div>

        <div className="flow-arrow">→</div>

        <div className="flow-step">
          <span>03</span>
          <strong>CLASSIFY</strong>
          <small>DL waste vision</small>
        </div>

        <div className="flow-arrow">→</div>

        <div className="flow-step">
          <span>04</span>
          <strong>ACT</strong>
          <small>Collection + recovery</small>
        </div>
      </section>
    </section>
  );
}

export default AiIntelligence;
